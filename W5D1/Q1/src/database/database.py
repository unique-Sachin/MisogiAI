"""Database connection and session management."""

import os
from typing import Generator
# External dependencies (may lack type stubs)
from sqlalchemy import create_engine, text  # type: ignore
from sqlalchemy.orm import sessionmaker, Session  # type: ignore
from sqlalchemy.pool import StaticPool  # type: ignore

from .models import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/medical_ai_db"
)

# For testing, use SQLite
if os.getenv("TESTING") == "true":
    DATABASE_URL = "sqlite:///./test_medical_ai.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
# Attempt to create engine for non-SQLite databases. Fallback gracefully to an in-file SQLite if the
# necessary DB driver (e.g. psycopg2) is missing or any error occurs during engine creation. This
# keeps the application functional in development environments where Postgres is not available.
else:
    try:
        engine = create_engine(DATABASE_URL)
    except ModuleNotFoundError:
        # psycopg2 or another DB-API driver missing – fallback to local SQLite file
        fallback_db = "sqlite:///./medical_ai.db"
        os.environ["DATABASE_URL"] = fallback_db
        DATABASE_URL = fallback_db  # type: ignore  # noqa: PLW0603
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Database manager for medical AI assistant."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception:
            return False


# Global database manager instance
db_manager = DatabaseManager() 