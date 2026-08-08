"""Background worker that periodically analyzes all active streams."""

import asyncio
import logging

from .. import models, schemas
from ..config import settings
from ..database import SessionLocal
from ..websocket_manager import manager
from .analysis_runner import run_analysis

logger = logging.getLogger(__name__)


class StreamMonitor:
    """Runs the analysis pipeline against every active stream on a fixed interval."""

    def __init__(self):
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        """Start the background polling loop."""
        if self._task is None:
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Cancel the background polling loop."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run_loop(self) -> None:
        while True:
            await self._analyze_all_active_streams()
            await asyncio.sleep(settings.analysis_interval_seconds)

    async def _analyze_all_active_streams(self) -> None:
        db = SessionLocal()
        try:
            streams = db.query(models.Stream).filter(models.Stream.is_active.is_(True)).all()
        finally:
            db.close()

        for stream in streams:
            await self._analyze_one(stream.id)

    async def _analyze_one(self, stream_id: int) -> None:
        db = SessionLocal()
        try:
            stream = db.get(models.Stream, stream_id)
            if stream is None or not stream.is_active:
                return
            try:
                analysis, alerts = await asyncio.to_thread(run_analysis, db, stream)
            except Exception:
                logger.exception("Analysis failed for stream %s (%s)", stream.id, stream.source_url)
                return

            await manager.broadcast(
                {
                    "type": "analysis",
                    "stream_id": stream.id,
                    "analysis": schemas.StreamAnalysisResponse.model_validate(analysis).model_dump(mode="json"),
                    "alerts": [schemas.AlertResponse.model_validate(a).model_dump(mode="json") for a in alerts],
                }
            )
        finally:
            db.close()


monitor = StreamMonitor()
