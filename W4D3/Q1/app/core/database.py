from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# SQLAlchemy database URL
DATABASE_URL = settings.database_url

# Create async engine and session maker
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Base class for models
Base = declarative_base()


async def get_db():
    """FastAPI dependency that provides an async database session."""
    async with AsyncSessionLocal() as session:
        yield session 