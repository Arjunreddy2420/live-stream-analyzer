"""Pydantic request/response schemas for the API layer."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StreamCreate(BaseModel):
    """Payload for registering a new stream."""

    name: str
    source_url: str
    protocol: str


class StreamResponse(BaseModel):
    """API representation of a registered stream."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_url: str
    protocol: str
    created_at: datetime
    is_active: bool
    last_updated: datetime | None = None


class CodecInfo(BaseModel):
    """API representation of detected video/audio codec information."""

    model_config = ConfigDict(from_attributes=True)

    video_codec: str | None = None
    video_resolution: str | None = None
    video_bitrate: int | None = None
    video_fps: float | None = None

    audio_codec: str | None = None
    audio_bitrate: int | None = None
    audio_channels: int | None = None
    audio_sample_rate: int | None = None


class StreamAnalysisResponse(BaseModel):
    """API representation of a stored stream analysis snapshot."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stream_id: int
    timestamp: datetime

    video_codec: str | None = None
    video_resolution: str | None = None
    video_bitrate: int | None = None
    video_fps: float | None = None

    audio_codec: str | None = None
    audio_bitrate: int | None = None
    audio_channels: int | None = None
    audio_sample_rate: int | None = None

    packet_loss: float | None = None
    jitter_ms: float | None = None


class AlertResponse(BaseModel):
    """API representation of a stored alert."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stream_id: int
    timestamp: datetime
    alert_type: str
    severity: str
    message: str


class SCTEMarkerResponse(BaseModel):
    """API representation of a detected SCTE marker."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    stream_id: int
    timestamp: datetime
    marker_type: str
    event_id: str | None = None
    marker_metadata: dict | None = None
