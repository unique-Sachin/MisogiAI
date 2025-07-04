from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_api_key
from app.dependencies import AuthContext
from app.models import APIKey, RoleEnum
from app.inspector.manager import manager

router = APIRouter(tags=["Inspector"], prefix="/inspector")


async def _authenticate_admin(websocket: WebSocket) -> Optional[AuthContext]:
    api_key_value = websocket.headers.get(settings.api_key_header)
    if not api_key_value:
        return None
    async with AsyncSessionLocal() as session:
        hashed = hash_api_key(api_key_value)
        result = await session.execute(
            select(APIKey).where(APIKey.hashed_key == hashed, APIKey.revoked == False)
        )
        api_key_obj = result.scalar_one_or_none()
        if api_key_obj and api_key_obj.role == RoleEnum.admin:
            return AuthContext(api_key_obj)
    return None


@router.websocket("/ws")
async def inspector_ws(websocket: WebSocket):
    auth = await _authenticate_admin(websocket)
    if auth is None:
        await websocket.close(code=1008)  # Policy Violation
        return

    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive; ignore incoming messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket) 