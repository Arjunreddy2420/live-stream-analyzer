"""Endpoints for retrieving and managing quality/codec alerts."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# TODO: GET /              - list alerts (optionally filtered by stream_id/severity)
# TODO: GET /{alert_id}    - fetch a single alert
# TODO: DELETE /{alert_id} - dismiss/clear an alert
