"""WebSocket endpoint for live stream/analysis/alert updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..websocket_manager import manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def stream_updates(websocket: WebSocket):
    """Clients connect here to receive live broadcasts of analysis results and alerts."""
    await manager.connect(websocket)
    try:
        while True:
            # Connection is push-only from the server; just drain any client pings.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
