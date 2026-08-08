"""Endpoints for retrieving and triggering codec/quality analysis results."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from .. import models, schemas
from ..database import get_db
from ..services.analysis_runner import run_analysis
from ..websocket_manager import manager

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.get("/{stream_id}", response_model=schemas.StreamAnalysisResponse)
def get_latest_analysis(stream_id: int, db: Session = Depends(get_db)):
    """Return the most recent analysis snapshot for a stream."""
    analysis = (
        db.query(models.StreamAnalysis)
        .filter(models.StreamAnalysis.stream_id == stream_id)
        .order_by(models.StreamAnalysis.timestamp.desc())
        .first()
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found for this stream")
    return analysis


@router.get("/{stream_id}/history", response_model=list[schemas.StreamAnalysisResponse])
def get_analysis_history(stream_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Return historical analysis snapshots for a stream, most recent first."""
    return (
        db.query(models.StreamAnalysis)
        .filter(models.StreamAnalysis.stream_id == stream_id)
        .order_by(models.StreamAnalysis.timestamp.desc())
        .limit(limit)
        .all()
    )


@router.post("/{stream_id}/run", response_model=schemas.StreamAnalysisResponse, status_code=201)
async def trigger_analysis(stream_id: int, db: Session = Depends(get_db)):
    """Run an on-demand codec/quality analysis pass for a stream and persist the result."""
    stream = db.get(models.Stream, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")

    try:
        analysis, alerts = await run_in_threadpool(run_analysis, db, stream)
    except Exception as exc:  # ffmpeg/ffprobe failures, unreachable source, etc.
        raise HTTPException(status_code=502, detail=f"Analysis failed: {exc}") from exc

    await manager.broadcast(
        {
            "type": "analysis",
            "stream_id": stream_id,
            "analysis": schemas.StreamAnalysisResponse.model_validate(analysis).model_dump(mode="json"),
            "alerts": [schemas.AlertResponse.model_validate(a).model_dump(mode="json") for a in alerts],
        }
    )
    return analysis
