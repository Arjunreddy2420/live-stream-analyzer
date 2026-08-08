"""Application configuration loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings.

    Values are sourced from environment variables, falling back to a local
    `.env` file (see `.env.example` at the repo root for the full key list).
    """

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/stream_analyzer"

    # API metadata
    api_title: str = "Live Stream Quality Analyzer"
    api_version: str = "1.0.0"

    # Stream ingest ports
    srt_listen_port: int = 9710
    rtmp_listen_port: int = 1935

    # Quality thresholds used by the quality analyzer / alerting logic
    min_bitrate: int = 500
    max_bitrate: int = 50000
    min_fps: int = 24
    max_packet_loss: float = 1.0

    # How often the background monitor re-analyzes each active stream, in seconds.
    analysis_interval_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
