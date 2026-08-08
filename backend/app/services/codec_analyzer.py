"""Video/audio codec detection via ffprobe (through ffmpeg-python)."""

from dataclasses import dataclass
from enum import Enum

import ffmpeg


class VideoCodec(str, Enum):
    """Supported/recognized video codecs."""

    HEVC = "HEVC"
    H264 = "H264"
    VP9 = "VP9"
    AV1 = "AV1"
    MPEG2 = "MPEG2"
    UNKNOWN = "UNKNOWN"


class AudioCodec(str, Enum):
    """Supported/recognized audio codecs."""

    AAC = "AAC"
    AC3 = "AC3"
    EAC3 = "EAC3"
    DTS = "DTS"
    DOLBY_ATMOS = "DOLBY_ATMOS"
    FLAC = "FLAC"
    MP3 = "MP3"
    OPUS = "OPUS"
    UNKNOWN = "UNKNOWN"


_VIDEO_CODEC_MAP = {
    "hevc": VideoCodec.HEVC,
    "h265": VideoCodec.HEVC,
    "h264": VideoCodec.H264,
    "vp9": VideoCodec.VP9,
    "av1": VideoCodec.AV1,
    "mpeg2video": VideoCodec.MPEG2,
}

_AUDIO_CODEC_MAP = {
    "aac": AudioCodec.AAC,
    "ac3": AudioCodec.AC3,
    "eac3": AudioCodec.EAC3,
    "dts": AudioCodec.DTS,
    "flac": AudioCodec.FLAC,
    "mp3": AudioCodec.MP3,
    "opus": AudioCodec.OPUS,
}


@dataclass
class CodecInfo:
    """Detected codec and stream characteristics for a single analysis pass."""

    video_codec: VideoCodec = VideoCodec.UNKNOWN
    video_profile: str | None = None
    video_resolution: str | None = None
    video_bitrate: int | None = None
    video_fps: float | None = None

    audio_codec: AudioCodec = AudioCodec.UNKNOWN
    audio_bitrate: int | None = None
    audio_channels: int | None = None
    audio_sample_rate: int | None = None


def _parse_frame_rate(rate: str | None) -> float | None:
    """Convert an ffprobe fractional frame rate string (e.g. "30000/1001") to a float."""
    if not rate:
        return None
    num, _, den = rate.partition("/")
    try:
        num_f = float(num)
        den_f = float(den) if den else 1.0
        if den_f == 0:
            return None
        return round(num_f / den_f, 3)
    except ValueError:
        return None


def _map_audio_codec(codec_name: str | None, profile: str | None) -> AudioCodec:
    """Map an ffprobe audio codec name to our AudioCodec enum.

    ffprobe cannot reliably distinguish Dolby Atmos from a plain E-AC-3/TrueHD
    stream since Atmos is object-based metadata carried inside those codecs -
    we only flag it when ffprobe's profile field explicitly mentions it.
    """
    if not codec_name:
        return AudioCodec.UNKNOWN
    if profile and "atmos" in profile.lower():
        return AudioCodec.DOLBY_ATMOS
    return _AUDIO_CODEC_MAP.get(codec_name.lower(), AudioCodec.UNKNOWN)


class CodecAnalyzer:
    """Inspects a stream source and reports its video/audio codec information."""

    def analyze_stream(self, source_url: str) -> CodecInfo:
        """Probe `source_url` with ffprobe and return detected codec information."""
        probe = ffmpeg.probe(source_url)
        info = CodecInfo()

        format_bitrate = probe.get("format", {}).get("bit_rate")

        for stream in probe.get("streams", []):
            if stream.get("codec_type") == "video" and info.video_codec == VideoCodec.UNKNOWN:
                info.video_codec = _VIDEO_CODEC_MAP.get(
                    (stream.get("codec_name") or "").lower(), VideoCodec.UNKNOWN
                )
                info.video_profile = stream.get("profile")
                width, height = stream.get("width"), stream.get("height")
                info.video_resolution = f"{width}x{height}" if width and height else None
                bitrate = stream.get("bit_rate") or format_bitrate
                info.video_bitrate = int(int(bitrate) / 1000) if bitrate else None
                info.video_fps = _parse_frame_rate(stream.get("r_frame_rate"))

            elif stream.get("codec_type") == "audio" and info.audio_codec == AudioCodec.UNKNOWN:
                info.audio_codec = _map_audio_codec(stream.get("codec_name"), stream.get("profile"))
                bitrate = stream.get("bit_rate")
                info.audio_bitrate = int(int(bitrate) / 1000) if bitrate else None
                info.audio_channels = stream.get("channels")
                sample_rate = stream.get("sample_rate")
                info.audio_sample_rate = int(sample_rate) if sample_rate else None

        return info
