"""Tests for MPEG-TS packet parsing and continuity-counter loss detection."""

import pytest

from app.services.mpeg_ts_parser import MPEGTSParser


def make_packet(pid: int, continuity_counter: int, payload: bytes = b"", payload_unit_start: bool = False) -> bytes:
    """Build a minimal, valid 188-byte MPEG-TS packet for testing."""
    byte1 = (0x40 if payload_unit_start else 0x00) | ((pid >> 8) & 0x1F)
    byte2 = pid & 0xFF
    byte3 = 0x10 | (continuity_counter & 0x0F)  # adaptation_field_control = 01 (payload only)
    packet = bytes([0x47, byte1, byte2, byte3]) + payload[:184]
    return packet + bytes(188 - len(packet))


def test_parse_ts_packet_basic():
    parser = MPEGTSParser()
    packet = make_packet(pid=0x100, continuity_counter=3, payload=b"hello", payload_unit_start=True)

    parsed = parser.parse_ts_packet(packet)

    assert parsed["pid"] == 0x100
    assert parsed["continuity_counter"] == 3
    assert parsed["payload_unit_start"] is True
    assert parsed["payload"].startswith(b"hello")


def test_parse_ts_packet_rejects_bad_sync_byte():
    parser = MPEGTSParser()
    bad_packet = bytes([0x00]) + bytes(187)

    with pytest.raises(ValueError):
        parser.parse_ts_packet(bad_packet)


def test_count_continuity_errors_detects_gap():
    parser = MPEGTSParser()
    packets = [
        make_packet(pid=0x101, continuity_counter=0),
        make_packet(pid=0x101, continuity_counter=1),
        make_packet(pid=0x101, continuity_counter=4),  # counters 2 and 3 were dropped
    ]

    expected, lost = parser.count_continuity_errors(packets)

    assert expected == 3
    assert lost == 2


def test_count_continuity_errors_no_loss():
    parser = MPEGTSParser()
    packets = [make_packet(pid=0x101, continuity_counter=i % 16) for i in range(5)]

    expected, lost = parser.count_continuity_errors(packets)

    assert expected == 5
    assert lost == 0
