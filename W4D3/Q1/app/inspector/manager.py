from __future__ import annotations

import asyncio
import logging
from typing import List, Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket inspector connections and broadcasting."""

    def __init__(self):
        self._connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    @property
    def count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections.append(websocket)
        logger.info("Inspector connected, total=%s", self.count)
        await self.broadcast({"event": "inspector_connected", "connections": self.count})

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self._connections:
                self._connections.remove(websocket)
        logger.info("Inspector disconnected, total=%s", self.count)
        await self.broadcast({"event": "inspector_disconnected", "connections": self.count})

    async def broadcast(self, message: Any):
        """Broadcast a JSON-serialisable message to all active websockets."""
        stale: List[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                stale.append(ws)
            except Exception as exc:  # pragma: no cover
                logger.warning("Error sending to inspector WS: %s", exc)
        # Cleanup stale
        for ws in stale:
            await self.disconnect(ws)


manager = ConnectionManager() 