"""
STARTWISE AI — Pytest Conftest (Stage 7)

Provides AsyncClient, DB session, and authenticated user header fixtures for API tests.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from app.main import app
from app.database.session import engine, Base, AsyncSessionLocal
from app.core.security import create_access_token
from app.models.models import User, UserRole


from app.core.model_manager import ModelManager, get_model_manager

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Ensure DB schema is created for test run and ML models are loaded."""
    ModelManager.get_instance().initialize()

    def sync_schema(sync_conn):
        from sqlalchemy import inspect
        inspector = inspect(sync_conn)
        if "marketing_strategies" in inspector.get_table_names():
            cols = [c["name"] for c in inspector.get_columns("marketing_strategies")]
            if "user_id" not in cols:
                Base.metadata.tables["marketing_strategies"].drop(sync_conn, checkfirst=True)
        Base.metadata.create_all(sync_conn)

    async with engine.begin() as conn:
        await conn.run_sync(sync_schema)
    yield


@pytest_asyncio.fixture
async def db_session():
    """Provide transactional AsyncSession for test functions."""
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """HTTPX AsyncClient configured with ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create or return a test user in DB."""
    email = f"testuser_{uuid4().hex[:6]}@startwise.ai"
    user = User(
        full_name="Test User",
        email=email,
        hashed_password="$2b$12$eImiTXuWVxfM37uY4JANjO5E/XfR0hN5D1K6yF5Q3uGZ7v9u8",
        role=UserRole.user,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_token_headers(test_user):
    """Return Bearer token headers for test_user."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_user(db_session):
    """Create or return an admin user in DB."""
    email = f"admin_{uuid4().hex[:6]}@startwise.ai"
    user = User(
        full_name="Admin User",
        email=email,
        hashed_password="$2b$12$eImiTXuWVxfM37uY4JANjO5E/XfR0hN5D1K6yF5Q3uGZ7v9u8",
        role=UserRole.admin,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token_headers(admin_user):
    """Return Bearer token headers for admin_user."""
    token = create_access_token(subject=str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}
