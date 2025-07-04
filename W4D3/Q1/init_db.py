#!/usr/bin/env python3
"""
Database initialization script for MCP Discord Server
This script creates all the database tables and initial data
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_api_key, generate_api_key
from app.models import Tenant, APIKey, RoleEnum


async def init_database():
    """Initialize the database with tables and bootstrap data"""
    print("🗄️  Initializing MCP Discord Server Database")
    print("=" * 50)
    
    # Create engine
    engine = create_async_engine(settings.database_url, echo=True)
    
    # Create all tables
    print("📋 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    
    # Create bootstrap tenant and admin API key
    print("🔑 Creating bootstrap tenant and admin API key...")
    
    async with AsyncSession(engine) as session:
        # Create default tenant
        tenant = Tenant(
            name="Default Tenant",
            discord_bot_token="dummy-token-for-testing"
        )
        session.add(tenant)
        await session.flush()  # Get the tenant ID
        
        # Store tenant name before commit
        tenant_name = tenant.name
        tenant_id = tenant.id
        
        # Create bootstrap admin API key
        plain_key = "bootstrap-admin-key"
        hashed_key = hash_api_key(plain_key)
        
        admin_key = APIKey(
            tenant_id=tenant_id,
            name="Bootstrap Admin Key",
            hashed_key=hashed_key,
            role=RoleEnum.admin
        )
        session.add(admin_key)
        
        await session.commit()
        
        print(f"✅ Bootstrap tenant created: {tenant_name}")
        print(f"✅ Bootstrap admin API key created: {plain_key}")
        print("⚠️  This bootstrap key should be used to create your first real admin key!")
    
    await engine.dispose()
    
    print("\n🎉 Database initialization complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Start the server: python3 -m uvicorn app.main:app --reload")
    print("2. Create your first admin key using the bootstrap key")
    print("3. Use the test helper: python3 test_helper.py")


if __name__ == "__main__":
    asyncio.run(init_database()) 