from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_api_key
from app.models import APIKey, RoleEnum

api_key_header_scheme = APIKeyHeader(name=settings.api_key_header, auto_error=False)


class AuthContext:
    """Holds authenticated API key and its tenant/role."""

    def __init__(self, api_key_obj: APIKey):
        self.api_key = api_key_obj
        self.tenant = api_key_obj.tenant
        self.role = api_key_obj.role


async def get_current_auth(
    api_key_header: str | None = Depends(api_key_header_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    if not api_key_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    hashed = hash_api_key(api_key_header)
    result = await db.execute(
        select(APIKey)
        .options(selectinload(APIKey.tenant))
        .where((APIKey.hashed_key == hashed) & (APIKey.revoked.is_(False)))
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return AuthContext(obj)


def require_role(role: RoleEnum):
    async def _dependency(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        role_order = {RoleEnum.admin: 3, RoleEnum.write: 2, RoleEnum.read: 1}
        if role_order[auth.role] < role_order[role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions")
        return auth

    return _dependency 