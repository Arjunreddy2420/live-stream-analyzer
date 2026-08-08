"""Shared analysis pipeline used by both the on-demand API endpoint and the background monitor."""

from sqlalchemy.orm import Session

from .. import models
from .codec_analyzer import CodecAnalyzer
from .quality_analyzer import QualityAnalyzer

_codec_analyzer = CodecAnalyzer()
_quality_analyzer = QualityAnalyzer()


def run_analysis(db: Session, stream: models.Stream) -> tuple[models.StreamAnalysis, list[models.Alert]]:
    """Run codec + quality analysis for `stream`, persist the results, and raise alerts on threshold breach.

    This is blocking (shells out to ffmpeg/ffprobe) and should be run off the
    event loop, e.g. via starlette's `run_in_threadpool` or a plain thread/process.
    """
    codec_info = _codec_analyzer.analyze_stream(stream.source_url)
    quality = _quality_analyzer.analyze(stream.source_url)

    analysis = models.StreamAnalysis(
        stream_id=stream.id,
        video_codec=codec_info.video_codec.value,
        video_resolution=codec_info.video_resolution,
        video_bitrate=codec_info.video_bitrate,
        video_fps=codec_info.video_fps,
        audio_codec=codec_info.audio_codec.value,
        audio_bitrate=codec_info.audio_bitrate,
        audio_channels=codec_info.audio_channels,
        audio_sample_rate=codec_info.audio_sample_rate,
        packet_loss=quality.packet_loss,
        jitter_ms=quality.jitter_ms,
    )
    db.add(analysis)

    alerts = [
        models.Alert(
            stream_id=stream.id,
            alert_type="quality_threshold",
            severity="warning",
            message=reason,
        )
        for reason in quality.thresholds_breached
    ]
    db.add_all(alerts)

    db.commit()
    db.refresh(analysis)
    for alert in alerts:
        db.refresh(alert)

    return analysis, alerts
