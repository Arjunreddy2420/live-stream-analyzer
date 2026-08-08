"""Stream quality metric analysis service.

Combines ffprobe-derived metadata (resolution/fps, via CodecAnalyzer) with a
short raw MPEG-TS capture used to measure real packet loss (via TS
continuity-counter gaps, see MPEGTSParser) and local read jitter.
"""

import statistics
import subprocess
import time
from dataclasses import dataclass, field

from ..config import settings
from .codec_analyzer import CodecAnalyzer
from .mpeg_ts_parser import TS_PACKET_SIZE, MPEGTSParser


@dataclass
class QualityMetrics:
    """Computed quality metrics for a stream over a measurement window."""

    bitrate: int | None = None  # kbps, measured from the captured sample
    fps: float | None = None
    resolution: str | None = None
    packet_loss: float | None = None  # percent
    jitter_ms: float | None = None
    thresholds_breached: list[str] = field(default_factory=list)


class QualityAnalyzer:
    """Evaluates stream quality metrics against configured thresholds."""

    def __init__(self, codec_analyzer: CodecAnalyzer | None = None, ts_parser: MPEGTSParser | None = None):
        self._codec_analyzer = codec_analyzer or CodecAnalyzer()
        self._ts_parser = ts_parser or MPEGTSParser()

    def _capture_ts_packets(self, source_url: str, duration: float) -> tuple[list[bytes], float]:
        """Capture `duration` seconds of raw MPEG-TS from the source via ffmpeg, timing each read."""
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", source_url,
            "-t", str(duration),
            "-c", "copy",
            "-f", "mpegts",
            "-",
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        packets: list[bytes] = []
        arrival_deltas: list[float] = []
        last_read_time = None
        try:
            while True:
                chunk = proc.stdout.read(TS_PACKET_SIZE)
                if not chunk or len(chunk) < TS_PACKET_SIZE:
                    break
                now = time.monotonic()
                if last_read_time is not None:
                    arrival_deltas.append(now - last_read_time)
                last_read_time = now
                packets.append(chunk)
        finally:
            proc.stdout.close()
            proc.wait(timeout=5)

        jitter_ms = statistics.pstdev(arrival_deltas) * 1000 if len(arrival_deltas) > 1 else None
        return packets, jitter_ms

    def analyze(self, source_url: str, duration: float = 3.0) -> QualityMetrics:
        """Capture and evaluate quality metrics for the stream at `source_url`.

        `duration` controls how many seconds of the stream are sampled for
        packet-loss/jitter/bitrate measurement - longer samples are more
        accurate but take proportionally longer to run.
        """
        codec_info = self._codec_analyzer.analyze_stream(source_url)
        packets, jitter_ms = self._capture_ts_packets(source_url, duration)

        measured_bitrate = None
        packet_loss = None
        if packets:
            total_bytes = len(packets) * TS_PACKET_SIZE
            measured_bitrate = int((total_bytes * 8) / duration / 1000)  # kbps

            expected, lost = self._ts_parser.count_continuity_errors(packets)
            if expected + lost > 0:
                packet_loss = round((lost / (expected + lost)) * 100, 3)

        metrics = QualityMetrics(
            bitrate=measured_bitrate,
            fps=codec_info.video_fps,
            resolution=codec_info.video_resolution,
            packet_loss=packet_loss,
            jitter_ms=round(jitter_ms, 3) if jitter_ms is not None else None,
        )
        metrics.thresholds_breached = self._check_thresholds(metrics)
        return metrics

    def _check_thresholds(self, metrics: QualityMetrics) -> list[str]:
        """Compare measured metrics against configured quality thresholds."""
        breached = []
        if metrics.bitrate is not None:
            if metrics.bitrate < settings.min_bitrate:
                breached.append(f"bitrate {metrics.bitrate}kbps below minimum {settings.min_bitrate}kbps")
            elif metrics.bitrate > settings.max_bitrate:
                breached.append(f"bitrate {metrics.bitrate}kbps above maximum {settings.max_bitrate}kbps")
        if metrics.fps is not None and metrics.fps < settings.min_fps:
            breached.append(f"fps {metrics.fps} below minimum {settings.min_fps}")
        if metrics.packet_loss is not None and metrics.packet_loss > settings.max_packet_loss:
            breached.append(f"packet loss {metrics.packet_loss}% above maximum {settings.max_packet_loss}%")
        return breached
