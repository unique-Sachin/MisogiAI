import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.api_key import RoleEnum


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., description="Name for the new API key")
    role: RoleEnum = Field(..., description="Role for the new API key")


class APIKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: RoleEnum
    created_at: datetime
    revoked: bool

    model_config = {"from_attributes": True}


class APIKeyWithSecret(APIKeyResponse):
    secret: str = Field(..., description="Plaintext API key (returned once)") 