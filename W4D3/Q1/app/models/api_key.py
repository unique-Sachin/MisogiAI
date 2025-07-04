import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as PgEnum, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoleEnum(str, Enum):
    admin = "admin"
    write = "write"
    read = "read"


class APIKey(Base):
    __tablename__ = "api_keys"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    name: str = Column(String(255), nullable=False)
    hashed_key: str = Column(String(128), nullable=False, unique=True)
    role: RoleEnum = Column(PgEnum(RoleEnum, name="role_enum"), nullable=False)

    revoked: bool = Column(Boolean, default=False)
    revoked_at: datetime | None = Column(DateTime, nullable=True)

    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="api_keys") 