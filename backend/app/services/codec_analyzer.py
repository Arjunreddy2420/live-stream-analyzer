"""Video/audio codec detection service (Phase 2: ffmpeg-python-based implementation)."""

from dataclasses import dataclass
from enum import Enum


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


class CodecAnalyzer:
    """Inspects a stream source and reports its video/audio codec information."""

    def analyze_stream(self, source_url: str) -> CodecInfo:
        """Probe `source_url` and return detected codec information.

        # TODO (Phase 2): implement using ffmpeg-python / av to probe the
        # stream and populate a CodecInfo instance.
        """
        raise NotImplementedError("CodecAnalyzer.analyze_stream is not yet implemented")
