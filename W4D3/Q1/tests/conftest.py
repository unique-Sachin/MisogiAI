import asyncio
import uuid
import secrets

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import hash_api_key
from app.main import app as fastapi_app
from app.models import Tenant, APIKey, RoleEnum

DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(DATABASE_URL_TEST, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def session_maker(engine):
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
async def db(session_maker):
    async with session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch, session_maker):
    # Override database dependency
    async def _get_db_override():
        async with session_maker() as session:
            yield session
    
    fastapi_app.dependency_overrides[get_db] = _get_db_override
    
    # Disable audit middleware for tests
    fastapi_app.user_middleware = []


@pytest.fixture
async def admin_key(db):
    # Create tenant with unique name per test
    tenant_name = f"tenant-{uuid.uuid4().hex[:8]}"
    tenant = Tenant(name=tenant_name, discord_bot_token="dummy-token")
    db.add(tenant)
    await db.flush()

    # Generate unique API key per test
    plain_key = f"adminkey-{secrets.token_hex(8)}"
    api_key = APIKey(
        tenant_id=tenant.id,
        hashed_key=hash_api_key(plain_key),
        role=RoleEnum.admin,
    )
    db.add(api_key)
    await db.commit()
    return plain_key


@pytest.fixture
async def client():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as c:
        yield c 