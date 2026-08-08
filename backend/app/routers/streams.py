"""Endpoints for registering and managing monitored streams."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/v1/streams", tags=["streams"])


@router.post("/", response_model=schemas.StreamResponse, status_code=201)
def create_stream(payload: schemas.StreamCreate, db: Session = Depends(get_db)):
    """Register a new stream to be monitored."""
    stream = models.Stream(
        name=payload.name,
        source_url=payload.source_url,
        protocol=payload.protocol,
    )
    db.add(stream)
    db.commit()
    db.refresh(stream)
    return stream


@router.get("/", response_model=list[schemas.StreamResponse])
def list_streams(db: Session = Depends(get_db)):
    """List all registered streams."""
    return db.query(models.Stream).order_by(models.Stream.id).all()


@router.get("/{stream_id}", response_model=schemas.StreamResponse)
def get_stream(stream_id: int, db: Session = Depends(get_db)):
    """Fetch a single stream by id."""
    stream = db.get(models.Stream, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return stream


@router.delete("/{stream_id}", status_code=204)
def delete_stream(stream_id: int, db: Session = Depends(get_db)):
    """Remove a stream and its associated analyses/alerts/markers."""
    stream = db.get(models.Stream, stream_id)
    if stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    db.delete(stream)
    db.commit()
