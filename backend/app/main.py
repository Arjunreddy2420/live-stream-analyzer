"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import settings
from .database import engine
from .routers import alerts, analysis, streams, ws
from .services.monitor import monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown hook."""
    print(f"Starting {settings.api_title} v{settings.api_version}")
    models.Base.metadata.create_all(bind=engine)
    monitor.start()
    yield
    await monitor.stop()
    print("Shutting down")


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(streams.router)
app.include_router(analysis.router)
app.include_router(alerts.router)
app.include_router(ws.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Basic liveness check."""
    return {"status": "ok"}
