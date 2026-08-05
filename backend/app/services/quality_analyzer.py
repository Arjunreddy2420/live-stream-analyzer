"""Stream quality metric analysis service (Phase 2)."""

from dataclasses import dataclass


@dataclass
class QualityMetrics:
    """Computed quality metrics for a stream over a measurement window."""

    bitrate: int | None = None
    fps: float | None = None
    packet_loss: float | None = None
    jitter_ms: float | None = None
    resolution: str | None = None


class QualityAnalyzer:
    """Evaluates stream quality metrics against configured thresholds."""

    def analyze(self, stream_id: int) -> QualityMetrics:
        """Compute current quality metrics for the given stream.

        # TODO (Phase 2): implement metric collection (bitrate, fps,
        # packet loss, jitter) and threshold-based alert generation.
        """
        raise NotImplementedError("QualityAnalyzer.analyze is not yet implemented")
