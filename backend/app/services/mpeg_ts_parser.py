"""MPEG-TS packet parsing and SCTE-35 marker detection.

Implements enough of ISO/IEC 13818-1 (MPEG-TS) and SCTE-35 to locate the
PID carrying SCTE-35 data (via PAT -> PMT stream_type 0x86) and decode
splice_info_section messages carried on it.
"""

from dataclasses import dataclass, field

TS_PACKET_SIZE = 188
SYNC_BYTE = 0x47
SCTE35_STREAM_TYPE = 0x86


@dataclass
class SCTEMarker:
    """A decoded SCTE marker extracted from an MPEG-TS stream."""

    marker_type: str
    event_id: int | None = None
    pts_time: float | None = None
    duration: float | None = None
    out_of_network: bool | None = None
    metadata: dict = field(default_factory=dict)


class _BitReader:
    """Reads big-endian bit fields out of a byte buffer, MSB first."""

    def __init__(self, data: bytes):
        self._data = data
        self._bit_pos = 0

    def read_bits(self, n: int) -> int:
        """Read `n` bits and return them as an unsigned integer."""
        value = 0
        for _ in range(n):
            byte_index = self._bit_pos // 8
            bit_index = 7 - (self._bit_pos % 8)
            if byte_index >= len(self._data):
                raise ValueError("Ran out of data while reading SCTE-35 section")
            bit = (self._data[byte_index] >> bit_index) & 1
            value = (value << 1) | bit
            self._bit_pos += 1
        return value

    def skip_bits(self, n: int) -> None:
        """Advance the read position by `n` bits without returning a value."""
        self._bit_pos += n

    @property
    def byte_pos(self) -> int:
        """Current read position rounded down to a whole byte."""
        return self._bit_pos // 8


class MPEGTSParser:
    """Parses raw MPEG-TS packets and extracts SCTE-35 markers."""

    def parse_ts_packet(self, packet: bytes) -> dict:
        """Parse a single 188-byte MPEG-TS packet into its header/payload fields."""
        if len(packet) != TS_PACKET_SIZE:
            raise ValueError(f"Expected a {TS_PACKET_SIZE}-byte TS packet, got {len(packet)}")
        if packet[0] != SYNC_BYTE:
            raise ValueError(f"Invalid sync byte: {packet[0]:#x}")

        transport_error_indicator = bool(packet[1] & 0x80)
        payload_unit_start = bool(packet[1] & 0x40)
        pid = ((packet[1] & 0x1F) << 8) | packet[2]
        adaptation_field_control = (packet[3] & 0x30) >> 4
        continuity_counter = packet[3] & 0x0F

        offset = 4
        if adaptation_field_control in (2, 3):  # adaptation field present
            adaptation_field_length = packet[4]
            offset += 1 + adaptation_field_length

        payload = packet[offset:] if adaptation_field_control in (1, 3) else b""

        return {
            "transport_error_indicator": transport_error_indicator,
            "payload_unit_start": payload_unit_start,
            "pid": pid,
            "adaptation_field_control": adaptation_field_control,
            "continuity_counter": continuity_counter,
            "payload": payload,
        }

    def count_continuity_errors(self, packets: list[bytes]) -> tuple[int, int]:
        """Count expected vs. lost packets using each PID's continuity_counter.

        The continuity_counter is a 4-bit value (0-15) that increments by one
        for every packet carrying a payload on a given PID. A gap larger than
        1 (mod 16) means intermediate packets were dropped in transit - this
        is the standard way to detect packet loss in an MPEG-TS stream.
        Returns (total_expected, total_lost).
        """
        last_counter: dict[int, int] = {}
        total_expected = 0
        total_lost = 0

        for raw in packets:
            try:
                parsed = self.parse_ts_packet(raw)
            except ValueError:
                continue
            if parsed["adaptation_field_control"] not in (1, 3):
                continue  # no payload, continuity_counter does not advance
            pid = parsed["pid"]
            counter = parsed["continuity_counter"]
            total_expected += 1

            if pid in last_counter:
                gap = (counter - last_counter[pid]) % 16
                if gap == 0:
                    pass  # duplicate packet, not loss
                elif gap > 1:
                    total_lost += gap - 1
            last_counter[pid] = counter

        return total_expected, total_lost

    def _find_scte35_pid(self, packets: list[bytes]) -> int | None:
        """Walk PAT -> PMT to find the elementary stream PID carrying SCTE-35 (stream_type 0x86)."""
        pmt_pid = None
        for raw in packets:
            try:
                parsed = self.parse_ts_packet(raw)
            except ValueError:
                continue
            if parsed["pid"] != 0 or not parsed["payload"] or not parsed["payload_unit_start"]:
                continue
            payload = parsed["payload"]
            pointer_field = payload[0]
            section = payload[1 + pointer_field :]
            if not section or section[0] != 0x00:  # PAT table_id
                continue
            section_length = ((section[1] & 0x0F) << 8) | section[2]
            program_data = section[8 : 3 + section_length - 4]  # strip header + trailing CRC
            for i in range(0, len(program_data) - 3, 4):
                program_number = (program_data[i] << 8) | program_data[i + 1]
                pid = ((program_data[i + 2] & 0x1F) << 8) | program_data[i + 3]
                if program_number != 0:  # skip the network PID entry
                    pmt_pid = pid
                    break
            if pmt_pid is not None:
                break

        if pmt_pid is None:
            return None

        for raw in packets:
            try:
                parsed = self.parse_ts_packet(raw)
            except ValueError:
                continue
            if parsed["pid"] != pmt_pid or not parsed["payload"] or not parsed["payload_unit_start"]:
                continue
            payload = parsed["payload"]
            pointer_field = payload[0]
            section = payload[1 + pointer_field :]
            if not section or section[0] != 0x02:  # PMT table_id
                continue
            section_length = ((section[1] & 0x0F) << 8) | section[2]
            program_info_length = ((section[10] & 0x0F) << 8) | section[11]
            cursor = 12 + program_info_length
            end = 3 + section_length - 4  # exclude trailing CRC
            while cursor + 5 <= end:
                stream_type = section[cursor]
                elementary_pid = ((section[cursor + 1] & 0x1F) << 8) | section[cursor + 2]
                es_info_length = ((section[cursor + 3] & 0x0F) << 8) | section[cursor + 4]
                if stream_type == SCTE35_STREAM_TYPE:
                    return elementary_pid
                cursor += 5 + es_info_length
            break

        return None

    def _decode_splice_info_section(self, section: bytes) -> SCTEMarker | None:
        """Decode a single SCTE-35 splice_info_section into an SCTEMarker."""
        if not section or section[0] != 0xFC:
            return None

        reader = _BitReader(section)
        reader.skip_bits(8)  # table_id
        reader.skip_bits(1)  # section_syntax_indicator
        reader.skip_bits(1)  # private_indicator
        reader.skip_bits(2)  # reserved
        reader.skip_bits(12)  # section_length
        reader.skip_bits(8)  # protocol_version
        reader.skip_bits(1)  # encrypted_packet
        reader.skip_bits(6)  # encryption_algorithm
        pts_adjustment = reader.read_bits(33)
        reader.skip_bits(8)  # cw_index
        reader.skip_bits(12)  # tier
        reader.skip_bits(12)  # splice_command_length
        splice_command_type = reader.read_bits(8)

        metadata = {"pts_adjustment": pts_adjustment}

        if splice_command_type == 0x05:  # splice_insert
            event_id = reader.read_bits(32)
            cancel = bool(reader.read_bits(1))
            reader.skip_bits(7)
            if cancel:
                return SCTEMarker(
                    marker_type="splice_insert",
                    event_id=event_id,
                    metadata={**metadata, "cancelled": True},
                )

            out_of_network = bool(reader.read_bits(1))
            program_splice_flag = bool(reader.read_bits(1))
            duration_flag = bool(reader.read_bits(1))
            splice_immediate_flag = bool(reader.read_bits(1))
            reader.skip_bits(4)

            pts_time = None
            if program_splice_flag and not splice_immediate_flag:
                time_specified = bool(reader.read_bits(1))
                if time_specified:
                    reader.skip_bits(6)
                    pts_time = reader.read_bits(33) / 90000.0
                else:
                    reader.skip_bits(7)

            duration = None
            if duration_flag:
                reader.skip_bits(1)  # auto_return
                reader.skip_bits(6)  # reserved
                duration = reader.read_bits(33) / 90000.0

            return SCTEMarker(
                marker_type="splice_insert",
                event_id=event_id,
                pts_time=pts_time,
                duration=duration,
                out_of_network=out_of_network,
                metadata=metadata,
            )

        if splice_command_type == 0x06:  # time_signal
            time_specified = bool(reader.read_bits(1))
            pts_time = None
            if time_specified:
                reader.skip_bits(6)
                pts_time = reader.read_bits(33) / 90000.0
            return SCTEMarker(marker_type="time_signal", pts_time=pts_time, metadata=metadata)

        return SCTEMarker(marker_type=f"splice_command_0x{splice_command_type:02x}", metadata=metadata)

    def detect_scte35_markers(self, packets: list[bytes]) -> list[SCTEMarker]:
        """Scan a sequence of MPEG-TS packets for SCTE-35 splice markers."""
        scte_pid = self._find_scte35_pid(packets)
        if scte_pid is None:
            return []

        markers = []
        for raw in packets:
            try:
                parsed = self.parse_ts_packet(raw)
            except ValueError:
                continue
            if parsed["pid"] != scte_pid or not parsed["payload"] or not parsed["payload_unit_start"]:
                continue
            payload = parsed["payload"]
            pointer_field = payload[0]
            section = payload[1 + pointer_field :]
            try:
                marker = self._decode_splice_info_section(section)
            except ValueError:
                continue
            if marker is not None:
                markers.append(marker)

        return markers
