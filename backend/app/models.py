"""SQLAlchemy ORM models for streams, analysis results, alerts, and SCTE markers."""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .database import Base


def _utcnow() -> datetime:
    """Return the current UTC time; used as a shared default for timestamp columns."""
    return datetime.now(timezone.utc)


class Stream(Base):
    """A registered live stream source (SRT, RTMP, etc.) being monitored."""

    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    protocol = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_updated = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    analyses = relationship("StreamAnalysis", back_populates="stream", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="stream", cascade="all, delete-orphan")
    scte_markers = relationship("SCTEMarker", back_populates="stream", cascade="all, delete-orphan")


class StreamAnalysis(Base):
    """A point-in-time codec/quality analysis snapshot for a stream."""

    __tablename__ = "stream_analyses"

    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    # Video info
    video_codec = Column(String, nullable=True)
    video_resolution = Column(String, nullable=True)
    video_bitrate = Column(Integer, nullable=True)
    video_fps = Column(Float, nullable=True)

    # Audio info
    audio_codec = Column(String, nullable=True)
    audio_bitrate = Column(Integer, nullable=True)
    audio_channels = Column(Integer, nullable=True)
    audio_sample_rate = Column(Integer, nullable=True)

    # Quality metrics
    packet_loss = Column(Float, nullable=True)
    jitter_ms = Column(Float, nullable=True)

    stream = relationship("Stream", back_populates="analyses")


class Alert(Base):
    """A quality or codec alert raised for a stream."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)

    stream = relationship("Stream", back_populates="alerts")


class SCTEMarker(Base):
    """A SCTE-35/SCTE-104 marker detected in a stream's MPEG-TS payload."""

    __tablename__ = "scte_markers"

    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    marker_type = Column(String, nullable=False)
    event_id = Column(String, nullable=True)
    marker_metadata = Column(JSON, nullable=True)

    stream = relationship("Stream", back_populates="scte_markers")
