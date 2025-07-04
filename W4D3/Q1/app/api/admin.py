from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import generate_api_key, hash_api_key
from app.dependencies import require_role
from app.models import APIKey, RoleEnum
from app.schemas import APIKeyCreateRequest, APIKeyWithSecret, APIKeyResponse
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter(prefix="/admin", tags=["Admin"])

endpoint_limit = f"{settings.rate_limit_per_endpoint}/minute"


@router.post("/api-keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
@limiter.limit(endpoint_limit)
async def create_api_key(
    request: Request,
    payload: APIKeyCreateRequest,
    auth=Depends(require_role(RoleEnum.admin)),
    db: AsyncSession = Depends(get_db),
):
    raw_key = generate_api_key()
    hashed = hash_api_key(raw_key)

    api_key_obj = APIKey(
        tenant_id=auth.tenant.id,
        name=payload.name,
        hashed_key=hashed,
        role=payload.role,
    )
    db.add(api_key_obj)
    await db.commit()
    await db.refresh(api_key_obj)

    return APIKeyWithSecret(
        id=api_key_obj.id,
        name=api_key_obj.name,
        role=api_key_obj.role,
        created_at=api_key_obj.created_at,
        revoked=api_key_obj.revoked,
        secret=raw_key,
    )


@router.get("/api-keys", response_model=list[APIKeyResponse])
@limiter.limit(endpoint_limit)
async def list_api_keys(
    request: Request,
    auth=Depends(require_role(RoleEnum.admin)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where(APIKey.tenant_id == auth.tenant.id)
    )

    api_keys = result.scalars().all()
    return api_keys


@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(endpoint_limit)
async def revoke_api_key(
    request: Request,
    api_key_id: uuid.UUID,
    auth=Depends(require_role(RoleEnum.admin)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where((APIKey.id == api_key_id) & (APIKey.tenant_id == auth.tenant.id))
    )
    api_key_obj = result.scalar_one_or_none()
    if api_key_obj is None:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key_obj.revoked:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    api_key_obj.revoked = True
    api_key_obj.revoked_at = datetime.utcnow()
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT) 