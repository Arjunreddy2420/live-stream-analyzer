"""Endpoints for registering and managing monitored streams."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/streams", tags=["streams"])

# TODO: POST /            - register a new stream (StreamCreate -> StreamResponse)
# TODO: GET /             - list all registered streams
# TODO: GET /{stream_id}  - fetch a single stream by id
# TODO: DELETE /{stream_id} - remove a stream
