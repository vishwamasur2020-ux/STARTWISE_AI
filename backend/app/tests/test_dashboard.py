"""
STARTWISE AI -- Dashboard Test Suite (Stage 10)
Pytest tests for aggregated AI Business Intelligence Dashboard endpoints.
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4

@pytest.mark.asyncio
async def test_get_empty_dashboard(client: AsyncClient, user_token_headers: dict):
    """User with 0 startups gets an empty dashboard response (has_startups=False)."""
    res = await client.get("/api/v1/dashboard", headers=user_token_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["has_startups"] is False
    assert data["has_prediction"] is False
    assert data["startup"] is None
    assert data["completeness"]["percentage"] == 0

@pytest.mark.asyncio
async def test_get_dashboard_with_full_intelligence(client: AsyncClient, user_token_headers: dict):
    """Full workflow: startup -> prediction -> franchise -> marketing -> dashboard."""
    # 1. Run prediction for startup
    st_payload = {
        "business_name": "Apex Cloud Tech",
        "business_category": "Technology",
        "business_model": "SaaS",
        "investment_amount": 1000000.0,
        "expected_monthly_revenue": 300000.0,
        "expected_monthly_expenses": 120000.0,
        "location": "Bengaluru",
        "target_customer": "Enterprise Software",
        "experience_years": 5,
    }
    res_pred = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    import sys
    sys.stderr.write(f"\nPRED RES: {res_pred.status_code} {res_pred.text}\n")
    assert res_pred.status_code == 201, f"Prediction failed ({res_pred.status_code}): {res_pred.text}"
    startup_id = res_pred.json()["startup_id"]

    # 2. Generate Franchise Recs
    rec_payload = {
        "startup_id": startup_id,
        "budget": 1000000.0,
        "business_category": "Technology",
        "location": "Bengaluru",
    }
    res_rec = await client.post("/api/v1/recommendations/franchises", json=rec_payload, headers=user_token_headers)
    import sys
    sys.stderr.write(f"\nREC RES: {res_rec.status_code} {res_rec.text}\n")
    assert res_rec.status_code == 200, f"Recs failed ({res_rec.status_code}): {res_rec.text}"

    # 3. Generate Marketing Strategy
    res_mkt = await client.post("/api/v1/marketing/analyze", json={"startup_id": startup_id}, headers=user_token_headers)
    print("MKT RES:", res_mkt.status_code, res_mkt.text)
    assert res_mkt.status_code == 201, f"Marketing failed ({res_mkt.status_code}): {res_mkt.text}"

    # 4. Fetch Dashboard
    res_dash = await client.get("/api/v1/dashboard", headers=user_token_headers)
    assert res_dash.status_code == 200
    data = res_dash.json()
    print("DASH DATA:", data)

    try:
        import sys
        sys.stderr.write(f"\nDASH DATA: {data}\n")
        assert data["has_startups"] is True
        assert data["has_prediction"] is True
        assert data["startup"]["id"] == startup_id
        assert data["prediction"]["business_score"] > 0
        assert data["financial"]["monthly_profit"] > 0
        assert data["financial"]["annual_profit"] > 0
        assert len(data["health_dimensions"]) == 6
        assert data["marketing"] is not None
    except Exception as e:
        import sys, traceback
        sys.stderr.write(f"\nEXC: {type(e)} {e}\n")
        traceback.print_exc()
        raise e

@pytest.mark.asyncio
async def test_get_dashboard_specific_startup(client: AsyncClient, user_token_headers: dict):
    """Retrieve dashboard for specific startup ID."""
    st_payload = {
        "business_name": "Urban Cafe",
        "business_category": "Food",
        "business_model": "Cafe",
        "investment_amount": 500000.0,
        "expected_monthly_revenue": 150000.0,
        "expected_monthly_expenses": 80000.0,
        "location": "Mumbai",
        "target_customer": "General Public",
    }
    res_pred = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    assert res_pred.status_code == 201, f"Failed prediction: {res_pred.text}"
    startup_id = res_pred.json()["startup_id"]

    res_dash = await client.get(f"/api/v1/dashboard/startups/{startup_id}", headers=user_token_headers)
    assert res_dash.status_code == 200
    assert res_dash.json()["startup"]["id"] == startup_id

@pytest.mark.asyncio
async def test_dashboard_statistics(client: AsyncClient, user_token_headers: dict):
    """Fetch user dashboard statistics."""
    res_stats = await client.get("/api/v1/dashboard/statistics", headers=user_token_headers)
    assert res_stats.status_code == 200
    data = res_stats.json()
    assert "total_startups" in data
    assert "completed_analyses" in data
    assert "average_business_score" in data

@pytest.mark.asyncio
async def test_dashboard_forbidden_cross_user_access(client: AsyncClient, user_token_headers: dict):
    """User B cannot access User A's startup dashboard."""
    # User A creates prediction
    st_payload = {
        "business_name": "User A Venture",
        "business_category": "Services",
        "business_model": "Consulting",
        "investment_amount": 400000.0,
        "expected_monthly_revenue": 120000.0,
        "expected_monthly_expenses": 70000.0,
        "location": "Delhi",
        "target_customer": "B2B Clients",
    }
    res_a = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    assert res_a.status_code == 201, f"Failed prediction: {res_a.text}"
    startup_id = res_a.json()["startup_id"]

    # User B login
    email_b = f"userB_dash_{uuid4().hex[:6]}@example.com"
    pass_b = "Password123!"
    await client.post("/api/v1/auth/register", json={
        "full_name": "User B",
        "email": email_b,
        "password": pass_b,
        "confirm_password": pass_b,
    })
    res_login = await client.post("/api/v1/auth/login", json={"email": email_b, "password": pass_b})
    token_b = res_login.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B requests User A's startup dashboard -> 403 Forbidden
    res_forb = await client.get(f"/api/v1/dashboard/startups/{startup_id}", headers=headers_b)
    assert res_forb.status_code == 403, f"Got {res_forb.status_code}: {res_forb.text}"
