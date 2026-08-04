"""
STARTWISE AI — Database Session Management
Async SQLAlchemy 2.0 engine + session factory for Neon PostgreSQL.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# ─── Declarative Base ────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ─── Async Engine ────────────────────────────────────────────────────────────
db_url = settings.DATABASE_URL
is_sqlite = "sqlite" in db_url or "username:password" in db_url or "ep-xxx" in db_url

if is_sqlite:
    db_url = "sqlite+aiosqlite:///./startwise.db"
    logger.info("Using local SQLite database (startwise.db)")
    engine: AsyncEngine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
    )
else:
    logger.info("Using PostgreSQL database")
    engine: AsyncEngine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        poolclass=NullPool,  # Neon serverless
    )

# ─── Session Factory ─────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ─── Dependency ──────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
