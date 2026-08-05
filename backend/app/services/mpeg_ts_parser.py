"""MPEG-TS packet parsing and SCTE-35/SCTE-104 marker detection (Phase 2)."""

from dataclasses import dataclass


@dataclass
class SCTEMarker:
    """A decoded SCTE marker extracted from an MPEG-TS stream."""

    marker_type: str
    event_id: str | None = None
    pts: int | None = None
    duration: float | None = None
    metadata: dict | None = None


class MPEGTSParser:
    """Parses raw MPEG-TS packets and extracts SCTE-35/SCTE-104 markers."""

    def parse_ts_packet(self, packet: bytes) -> dict:
        """Parse a single 188-byte MPEG-TS packet into its header/payload fields.

        # TODO (Phase 2): implement MPEG-TS packet header parsing
        # (sync byte, PID, adaptation field, payload).
        """
        raise NotImplementedError("MPEGTSParser.parse_ts_packet is not yet implemented")

    def detect_scte35_markers(self, packets: list[bytes]) -> list[SCTEMarker]:
        """Scan a sequence of MPEG-TS packets for SCTE-35 splice markers.

        # TODO (Phase 2): implement SCTE-35 splice_info_section decoding.
        """
        raise NotImplementedError("MPEGTSParser.detect_scte35_markers is not yet implemented")
