"""
STARTWISE AI — Stage 14 Production Readiness & Health Test Suite
Tests health check endpoints, security headers, authentication barriers, and error isolation.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_fast_health_check():
    """Verify GET /health returns 200 and healthy status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_detailed_api_health_check():
    """Verify GET /api/health returns detailed services breakdown."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ("healthy", "degraded")
        services = data["services"]
        assert "database" in services
        assert "ml_engine" in services
        assert "ml_models" in services
        assert "xai_engine" in services
        assert "email_service" in services
        assert "report_service" in services


@pytest.mark.asyncio
async def test_production_security_headers():
    """Verify all HTTP responses carry modern defense-in-depth security headers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        headers = res.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert headers.get("X-XSS-Protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_unauthenticated_api_barrier():
    """Verify sensitive business endpoints strictly require valid JWT authorization."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Dashboard
        r = await client.get("/api/v1/dashboard")
        assert r.status_code in (401, 403)

        # Admin
        r = await client.get("/api/v1/admin/users")
        assert r.status_code in (401, 403)

        # Explainability
        r = await client.get("/api/v1/explainability/00000000-0000-0000-0000-000000000000")
        assert r.status_code in (401, 403)

        # Recommendations
        r = await client.post("/api/v1/recommendations/franchises", json={"startup_id": "00000000-0000-0000-0000-000000000000"})
        assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_malformed_token_rejection():
    """Verify malformed or forged JWT tokens are rejected cleanly."""
    transport = ASGITransport(app=app)
    headers = {"Authorization": "Bearer forged.invalid.token.12345"}
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/dashboard", headers=headers)
        assert r.status_code in (401, 403)
