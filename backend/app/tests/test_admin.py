"""
STARTWISE AI — Admin Panel Tests (Stage 12)
Unit & integration tests verifying RBAC enforcement and Admin API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_dashboard_unauthorized(client: AsyncClient):
    """Accessing /api/v1/admin/dashboard without auth returns 401."""
    resp = await client.get("/api/v1/admin/dashboard")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_dashboard_forbidden_for_user(client: AsyncClient, user_token_headers: dict):
    """Accessing /api/v1/admin/dashboard as normal user returns 403."""
    resp = await client.get("/api/v1/admin/dashboard", headers=user_token_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_dashboard_success(client: AsyncClient, admin_token_headers: dict):
    """Accessing /api/v1/admin/dashboard as admin returns 200 with stats."""
    resp = await client.get("/api/v1/admin/dashboard", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert "startups" in data
    assert "predictions" in data
    assert "franchises" in data
    assert "reports" in data
    assert isinstance(data["users"]["total"], int)
    assert isinstance(data["predictions"]["average_score"], (int, float))


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, admin_token_headers: dict):
    """Admin can list users with pagination."""
    resp = await client.get("/api/v1/admin/users?page=1&per_page=10", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_admin_user_status_and_role(client: AsyncClient, admin_token_headers: dict, test_user):
    """Admin can update user status and role."""
    # Deactivate test user
    resp = await client.patch(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": False},
        headers=admin_token_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    # Reactivate test user
    resp = await client.patch(
        f"/api/v1/admin/users/{test_user.id}/status",
        json={"is_active": True},
        headers=admin_token_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True


@pytest.mark.asyncio
async def test_admin_list_startups(client: AsyncClient, admin_token_headers: dict):
    """Admin can list startups."""
    resp = await client.get("/api/v1/admin/startups", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_admin_list_predictions(client: AsyncClient, admin_token_headers: dict):
    """Admin can list predictions."""
    resp = await client.get("/api/v1/admin/predictions", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_admin_franchise_crud(client: AsyncClient, admin_token_headers: dict):
    """Admin can create, toggle status, and delete a franchise."""
    # Create
    create_payload = {
        "franchise_name": "Test Franchise Admin",
        "industry": "Food & Beverage",
        "business_model": "QSR",
        "minimum_investment": 500000,
        "maximum_investment": 1500000,
        "roi": 25.5,
        "risk_level": "Low",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "experience_required": 1,
        "market_demand": 8,
        "description": "Test franchise description",
        "is_active": True,
    }
    create_resp = await client.post(
        "/api/v1/admin/franchises",
        json=create_payload,
        headers=admin_token_headers,
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    fid = created["id"]
    assert created["franchise_name"] == "Test Franchise Admin"

    # Toggle status
    status_resp = await client.patch(
        f"/api/v1/admin/franchises/{fid}/status",
        json={"is_active": False},
        headers=admin_token_headers,
    )
    assert status_resp.status_code == 200
    assert status_resp.json()["is_active"] is False

    # Delete
    del_resp = await client.delete(
        f"/api/v1/admin/franchises/{fid}",
        headers=admin_token_headers,
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True


@pytest.mark.asyncio
async def test_admin_ml_info(client: AsyncClient, admin_token_headers: dict):
    """Admin can view ML model health status."""
    resp = await client.get("/api/v1/admin/ml", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "models" in data
    assert "preprocessors" in data
    assert "services" in data
    assert len(data["models"]) == 4


@pytest.mark.asyncio
async def test_admin_audit_logs(client: AsyncClient, admin_token_headers: dict):
    """Admin can view audit logs."""
    resp = await client.get("/api/v1/admin/audit-logs", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_admin_analytics(client: AsyncClient, admin_token_headers: dict):
    """Admin can view analytics."""
    resp = await client.get("/api/v1/admin/analytics?group_by=day", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_growth" in data
    assert "startup_creation" in data
    assert "risk_distribution" in data


@pytest.mark.asyncio
async def test_admin_settings_no_secrets(client: AsyncClient, admin_token_headers: dict):
    """Admin settings returns safe config without leaking secrets."""
    resp = await client.get("/api/v1/admin/settings", headers=admin_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "platform" in data
    assert "email" in data
    assert "ml" in data
    assert "security" in data
    # Verify no raw secret is leaked
    assert "RESEND_API_KEY" not in str(data)
    assert "DATABASE_URL" not in str(data) or "••••" in str(data)
