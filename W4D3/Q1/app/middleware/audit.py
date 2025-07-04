from __future__ import annotations

from datetime import datetime
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.security import hash_api_key
from app.models import APIKey, AuditLog
from app.inspector.manager import manager as inspector_manager


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware that stores an audit log entry for every HTTP request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        start = datetime.utcnow()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            # Create audit log entry even if an exception occurred (response may be None)
            status_code = response.status_code if response else 500
            await self._write_audit_log(request, status_code, start)

    async def _write_audit_log(self, request: Request, status_code: int, timestamp: datetime):
        # Open new DB session so we are decoupled from endpoint transactions
        async with AsyncSessionLocal() as session:
            tenant_id = None
            api_key_id = None
            api_key_header = request.headers.get(settings.api_key_header)
            if api_key_header:
                hashed = hash_api_key(api_key_header)
                result = await session.execute(select(APIKey).where(APIKey.hashed_key == hashed))
                api_key_obj = result.scalar_one_or_none()
                if api_key_obj is not None:
                    api_key_id = api_key_obj.id
                    tenant_id = api_key_obj.tenant_id

            audit = AuditLog(
                tenant_id=tenant_id,
                api_key_id=api_key_id,
                timestamp=timestamp,
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code,
            )
            session.add(audit)
            try:
                await session.commit()
            except Exception:
                await session.rollback()

            # Broadcast to inspector
            await inspector_manager.broadcast(
                {
                    "event": "audit_log",
                    "timestamp": timestamp.isoformat(),
                    "tenant_id": str(tenant_id) if tenant_id else None,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                }
            ) 