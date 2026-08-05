# Live Stream Quality & Codec Analyzer

A monitoring tool for live video streams (SRT/RTMP) that inspects video/audio codec information, tracks quality metrics (bitrate, fps, packet loss, jitter), detects SCTE-35/SCTE-104 markers, and raises alerts when streams fall outside configured quality thresholds.

## Features

- Register and monitor multiple live stream sources (SRT, RTMP)
- Video/audio codec detection (HEVC, H.264, VP9, AV1, AAC, AC-3, E-AC-3, DTS, Dolby Atmos, and more)
- Real-time quality metrics: bitrate, fps, packet loss, jitter
- SCTE-35/SCTE-104 marker detection for ad insertion and program boundary events
- Threshold-based alerting
- Live updates over WebSocket
- REST API for stream, analysis, and alert management

## Quick Start

1. Copy the example environment file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Start the stack with Docker Compose:

   ```bash
   docker-compose up
   ```

3. The API is available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs` and a health check at `http://localhost:8000/health`.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # Settings loaded from .env
│   ├── database.py          # SQLAlchemy engine/session setup
│   ├── websocket_manager.py # WebSocket connection manager
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── services/            # Codec/quality analysis + MPEG-TS parsing
│   └── routers/             # API route definitions
├── tests/
└── requirements.txt
frontend/
└── src/
    ├── components/
    ├── pages/
    ├── services/
    └── utils/
docs/
└── CODEC_REFERENCE.md       # Video/audio codec and SCTE standards reference
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, PostgreSQL
- **Stream analysis**: ffmpeg-python, av, scapy, srt-python
- **Real-time**: WebSockets
- **Monitoring**: prometheus-client
- **Infra**: Docker Compose

See [`docs/CODEC_REFERENCE.md`](docs/CODEC_REFERENCE.md) for codec and SCTE standards background.

## Status

This project is in early scaffolding (Phase 1). Core services (`codec_analyzer`, `mpeg_ts_parser`, `quality_analyzer`) and API endpoints are stubbed out and will be implemented in Phase 2.
