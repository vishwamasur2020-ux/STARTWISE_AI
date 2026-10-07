"""
STARTWISE AI — AI Marketing Recommendation Engine Test Suite (Stage 9)

Comprehensive backend pytest suite for Stage 9 AI Marketing Engine:
  - Multi-factor channel scoring & dynamic explanations
  - Stage 7 prediction integration & risk/competition adaptations
  - Budget allocation calculation & scenario generation
  - Strategy generation, retrieval, and regeneration
  - Sub-resource endpoints (/channels, /plan, /content)
  - Prerequisite validation (400 Bad Request if Stage 7 prediction missing)
  - Security authorization guards (403 Forbidden for unauthorized users)
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_marketing_strategy_generation(client: AsyncClient, user_token_headers: dict):
    """Test generating a personalized marketing strategy after Stage 7 prediction."""
    # 1. Create a startup & run Stage 7 prediction
    st_payload = {
        "business_name": "Organic Juice Bar",
        "business_category": "Food",
        "business_model": "B2C Storefront",
        "investment_amount": 800000,
        "expected_monthly_revenue": 250000,
        "expected_monthly_expenses": 140000,
        "location": "Bengaluru",
        "target_customer": "Students & Fitness Enthusiasts",
    }
    res_st = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    assert res_st.status_code == 201
    startup_id = res_st.json()["startup_id"]

    # 2. Analyze & Generate Marketing Strategy
    mkt_payload = {"startup_id": startup_id}
    response = await client.post("/api/v1/marketing/analyze", json=mkt_payload, headers=user_token_headers)
    assert response.status_code == 201
    data = response.json()

    assert data["startup_id"] == startup_id
    assert 50.0 <= data["marketing_score"] <= 100.0
    assert data["total_recommended_budget"] > 0
    assert "recommended_channels" in data
    assert len(data["recommended_channels"]) == 5

    # Check Top #1 recommended channel details
    top1 = data["recommended_channels"][0]
    assert top1["ranking_position"] == 1
    assert top1["marketing_score"] > 0
    assert len(top1["explanation"]) > 0

    # Check budget scenarios
    assert "budget_allocation" in data
    scenarios = data["budget_allocation"]["scenarios"]
    assert "LOW_BUDGET" in scenarios
    assert "BALANCED" in scenarios
    assert "AGGRESSIVE" in scenarios

    # Check 30-day plan
    assert "thirty_day_plan" in data
    assert len(data["thirty_day_plan"]) == 4  # 4 Weeks


@pytest.mark.asyncio
async def test_get_and_regenerate_marketing_strategy(client: AsyncClient, user_token_headers: dict):
    """Test fetching latest marketing strategy and regenerating it."""
    # Create startup & prediction
    st_payload = {
        "business_name": "Tech Academy",
        "business_category": "Education",
        "investment_amount": 500000,
        "expected_monthly_revenue": 180000,
        "expected_monthly_expenses": 100000,
        "location": "Hyderabad",
        "target_customer": "Students",
    }
    res_st = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    startup_id = res_st.json()["startup_id"]

    # Generate initial strategy
    await client.post("/api/v1/marketing/analyze", json={"startup_id": startup_id}, headers=user_token_headers)

    # Get latest strategy
    res_get = await client.get(f"/api/v1/marketing/{startup_id}", headers=user_token_headers)
    assert res_get.status_code == 200
    assert res_get.json()["startup_id"] == startup_id

    # Regenerate strategy
    res_regen = await client.post(f"/api/v1/marketing/{startup_id}/regenerate", headers=user_token_headers)
    assert res_regen.status_code in [200, 201]
    assert res_regen.json()["startup_id"] == startup_id


@pytest.mark.asyncio
async def test_marketing_sub_resource_endpoints(client: AsyncClient, user_token_headers: dict):
    """Test sub-resource endpoints /channels, /plan, /content."""
    st_payload = {
        "business_name": "Glow Salon",
        "business_category": "Services",
        "investment_amount": 600000,
        "expected_monthly_revenue": 200000,
        "expected_monthly_expenses": 110000,
        "location": "Mumbai",
        "target_customer": "Women & Youth",
    }
    res_st = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    startup_id = res_st.json()["startup_id"]

    # Generate strategy
    await client.post("/api/v1/marketing/analyze", json={"startup_id": startup_id}, headers=user_token_headers)

    # Test /channels
    res_ch = await client.get(f"/api/v1/marketing/{startup_id}/channels", headers=user_token_headers)
    assert res_ch.status_code == 200
    assert isinstance(res_ch.json(), list)
    assert len(res_ch.json()) == 5

    # Test /plan
    res_plan = await client.get(f"/api/v1/marketing/{startup_id}/plan", headers=user_token_headers)
    assert res_plan.status_code == 200
    assert len(res_plan.json()) == 4

    # Test /content
    res_cnt = await client.get(f"/api/v1/marketing/{startup_id}/content", headers=user_token_headers)
    assert res_cnt.status_code == 200
    assert "content_pillars" in res_cnt.json()


@pytest.mark.asyncio
async def test_missing_prediction_prerequisite_error(client: AsyncClient, user_token_headers: dict):
    """Calling marketing analysis without Stage 7 prediction returns 400 Bad Request."""
    # Create startup idea manually without running Stage 7 prediction
    st_payload = {
        "business_name": "No Prediction Startup",
        "business_category": "Technology",
        "business_model": "SaaS",
        "investment_amount": 1000000.0,
        "expected_monthly_revenue": 300000.0,
        "preferred_location": "Bengaluru",
        "target_customers": "Enterprise",
    }
    res_st = await client.post("/api/v1/startups", json=st_payload, headers=user_token_headers)
    assert res_st.status_code == 201, f"Failed to create startup: {res_st.text}"
    startup_id = res_st.json()["id"]

    # Try generating marketing strategy -> 400 Bad Request
    res_mkt = await client.post("/api/v1/marketing/analyze", json={"startup_id": startup_id}, headers=user_token_headers)
    assert res_mkt.status_code == 400
    assert "Complete your AI startup analysis" in res_mkt.json()["detail"]


@pytest.mark.asyncio
async def test_marketing_forbidden_cross_user_access(client: AsyncClient, user_token_headers: dict):
    """User B cannot access or generate marketing strategy for User A's startup."""
    # User A creates prediction & marketing strategy
    st_payload = {
        "business_name": "User A Startup",
        "business_category": "Food",
        "business_model": "Cafe",
        "investment_amount": 400000,
        "expected_monthly_revenue": 120000,
        "expected_monthly_expenses": 70000,
        "location": "Chennai",
        "target_customer": "General Public",
    }
    res_a = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    assert res_a.status_code == 201, f"Failed prediction: {res_a.text}"
    startup_id = res_a.json()["startup_id"]
    res_m = await client.post("/api/v1/marketing/analyze", json={"startup_id": startup_id}, headers=user_token_headers)
    assert res_m.status_code == 201, f"Failed marketing: {res_m.text}"

    # Register & login User B
    email_b = f"userB_mkt_{uuid4().hex[:6]}@example.com"
    pass_b = "Password123!"
    await client.post("/api/v1/auth/register", json={
        "full_name": "User B",
        "email": email_b,
        "password": pass_b,
        "confirm_password": pass_b,
    })
    from app.database.session import AsyncSessionLocal
    from app.models.models import User
    from sqlalchemy import update
    async with AsyncSessionLocal() as session:
        await session.execute(update(User).where(User.email == email_b.lower()).values(email_verified=True, is_verified=True))
        await session.commit()

    res_login = await client.post("/api/v1/auth/login", json={"email": email_b, "password": pass_b})
    token_b = res_login.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User B requests User A's marketing strategy -> 403 Forbidden
    res_forb = await client.get(f"/api/v1/marketing/{startup_id}", headers=headers_b)
    assert res_forb.status_code == 403, f"Got {res_forb.status_code}: {res_forb.text}"
