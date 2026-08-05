"""Endpoints for retrieving codec/quality analysis results."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# TODO: GET /{stream_id}         - latest analysis snapshot for a stream
# TODO: GET /{stream_id}/history - historical analysis snapshots for a stream
# TODO: POST /{stream_id}/run    - trigger an on-demand analysis pass
