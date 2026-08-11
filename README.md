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

## Quick Start (Docker)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin) — no local Python, Node, or ffmpeg install needed, all of that runs inside the containers.

1. Copy the example environment file and adjust as needed:

   ```bash
   cp .env.example .env
   ```

2. Build and start the full stack (Postgres, backend, frontend, and a local `mediamtx` test source):

   ```bash
   docker compose up --build
   ```

   (Use `docker-compose` with a hyphen instead of `docker compose` if you have the older standalone Compose v1 CLI.) First build takes a few minutes — the backend image installs `ffmpeg` and Python dependencies, and the frontend image installs npm packages. Subsequent runs are much faster (`docker compose up` without `--build`).

3. Once it's up, check everything is healthy:

   ```bash
   docker compose ps
   ```

   You should see `postgres`, `backend`, `frontend`, and `mediamtx` all `Up` (Postgres shows `healthy`).

4. The API is available at `http://localhost:8000` (interactive docs at `/docs`, health check at `/health`), and the dashboard is available at `http://localhost:3000`.

5. To stop everything:

   ```bash
   docker compose down
   ```

### Running without Docker

Backend:

```bash
cd backend
pip install -r requirements.txt   # also requires the ffmpeg/ffprobe binaries on PATH
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Testing with a Local Stream

The stack includes a `mediamtx` service — a lightweight local RTMP/SRT server — so you can generate a synthetic test stream instead of depending on an external source.

**If you have `ffmpeg` installed locally**, push a test pattern into it directly:

```bash
# RTMP
ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=30 \
  -f lavfi -i sine=frequency=1000 \
  -c:v libx264 -b:v 2500k -c:a aac \
  -f flv rtmp://localhost:1935/live/test

# SRT
ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=30 \
  -f lavfi -i sine=frequency=1000 \
  -c:v libx264 -b:v 2500k -c:a aac \
  -f mpegts "srt://localhost:8890?streamid=publish:test"
```

**If you don't have `ffmpeg` installed locally**, the `backend` image already has it — run the push from a throwaway container on the same Docker network instead:

```bash
docker run -d --name mediamtx-test-push \
  --network live-stream-analyzer_default \
  live-stream-analyzer-backend \
  ffmpeg -re -f lavfi -i testsrc=size=1280x720:rate=30 \
  -f lavfi -i sine=frequency=1000 \
  -c:v libx264 -b:v 2500k -c:a aac \
  -f flv rtmp://mediamtx:1935/live/test

# stop it later with:
docker stop mediamtx-test-push && docker rm mediamtx-test-push
```

Then register a stream pointing at `rtmp://mediamtx:1935/live/test` (or the SRT equivalent) from the dashboard, or via:

```bash
curl -X POST http://localhost:8000/api/v1/streams/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Stream", "source_url": "rtmp://mediamtx:1935/live/test", "protocol": "RTMP"}'
```

The background monitor picks up active streams automatically (every `ANALYSIS_INTERVAL_SECONDS`), or click "Run Analysis" on the dashboard for an on-demand pass. Changing `-b:v`, `-r`, or the video codec mid-stream is a quick way to test quality/codec-drift detection. OBS Studio works as an alternative source if you'd rather push a real camera/screen capture.

## Project Structure

```
backend/
├── app/
│   ├── main.py                # FastAPI app entrypoint, lifespan, monitor startup
│   ├── config.py               # Settings loaded from .env
│   ├── database.py             # SQLAlchemy engine/session setup
│   ├── websocket_manager.py    # WebSocket connection manager
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── services/
│   │   ├── codec_analyzer.py    # ffprobe-based video/audio codec detection
│   │   ├── quality_analyzer.py  # bitrate/fps/packet-loss/jitter measurement
│   │   ├── mpeg_ts_parser.py    # MPEG-TS packet parsing + SCTE-35 decoding
│   │   ├── analysis_runner.py   # shared pipeline: analyze -> persist -> alert
│   │   └── monitor.py           # background loop that analyzes active streams
│   └── routers/                 # streams, analysis, alerts, ws (WebSocket)
├── tests/
└── requirements.txt
frontend/
└── src/
    ├── components/    # AddStreamForm, StreamCard, AlertFeed
    ├── pages/         # Dashboard
    ├── services/      # api.ts (REST), websocket.ts (live updates)
    └── utils/         # formatting helpers
docs/
└── CODEC_REFERENCE.md       # Video/audio codec and SCTE standards reference
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, PostgreSQL
- **Frontend**: React, TypeScript, Vite
- **Stream analysis**: ffmpeg-python / ffmpeg & ffprobe binaries, custom MPEG-TS/SCTE-35 parser
- **Real-time**: WebSockets
- **Monitoring**: prometheus-client
- **Infra**: Docker Compose (postgres, backend, frontend, mediamtx test source)

See [`docs/CODEC_REFERENCE.md`](docs/CODEC_REFERENCE.md) for codec and SCTE standards background.

## Status

Phase 2 core pipeline is implemented: stream registration, ffprobe-based codec detection, quality metrics (bitrate/fps measured live; packet loss measured via MPEG-TS continuity-counter gaps; jitter as a local-read-timing heuristic), SCTE-35 marker decoding, threshold-based alerting, a background monitor that re-analyzes active streams on an interval, live updates over WebSocket, and a React dashboard.

Known gaps / next steps:

- No DB migrations (Alembic) — tables are created via `Base.metadata.create_all()` on startup, fine for dev, not for evolving a production schema.
- SCTE-35 markers are decoded but not yet persisted to the `SCTEMarker` table or exposed via an API endpoint.
- Packet loss / jitter are measured from a short live capture per analysis pass, not continuously — good enough for spot checks and periodic monitoring, not a full transport-level capture pipeline.
- No authentication on the API or dashboard.
