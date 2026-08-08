"""Endpoints for retrieving and managing quality/codec alerts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("/", response_model=list[schemas.AlertResponse])
def list_alerts(
    stream_id: int | None = None,
    severity: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List alerts, optionally filtered by stream_id and/or severity."""
    query = db.query(models.Alert)
    if stream_id is not None:
        query = query.filter(models.Alert.stream_id == stream_id)
    if severity is not None:
        query = query.filter(models.Alert.severity == severity)
    return query.order_by(models.Alert.timestamp.desc()).limit(limit).all()


@router.get("/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Fetch a single alert by id."""
    alert = db.get(models.Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.delete("/{alert_id}", status_code=204)
def dismiss_alert(alert_id: int, db: Session = Depends(get_db)):
    """Dismiss (delete) an alert."""
    alert = db.get(models.Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
