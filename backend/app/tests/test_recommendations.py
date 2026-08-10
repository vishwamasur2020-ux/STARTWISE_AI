"""
STARTWISE AI — Franchise Recommendation API Test Suite (Stage 8)

Comprehensive backend pytest suite for Stage 8 AI Franchise Recommendation Engine:
  - Franchise catalog browsing, searching, and filtering
  - Categories & locations endpoints
  - Single franchise details retrieval
  - Personalized hybrid AI recommendation generation
  - Stage 7 prediction integration & dynamic ranking
  - Side-by-side comparison matrix
  - Security & cross-user access guards (403 Forbidden)
  - Recommendation history persistence and refresh
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_list_franchises(client: AsyncClient):
    """Verify listing franchises and filtering by category."""
    response = await client.get("/api/v1/franchises")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10

    # Filter by category Food
    res_food = await client.get("/api/v1/franchises?category=Food")
    assert res_food.status_code == 200
    food_list = res_food.json()
    assert all("food" in item["industry"].lower() for item in food_list)


@pytest.mark.asyncio
async def test_get_categories_and_locations(client: AsyncClient):
    """Verify unique categories and locations endpoints."""
    res_cat = await client.get("/api/v1/franchises/categories")
    assert res_cat.status_code == 200
    categories = res_cat.json()
    assert "Food" in categories or "Retail" in categories

    res_loc = await client.get("/api/v1/franchises/locations")
    assert res_loc.status_code == 200
    locations = res_loc.json()
    assert isinstance(locations, list)


@pytest.mark.asyncio
async def test_generate_recommendations(client: AsyncClient, user_token_headers: dict):
    """Generate personalized hybrid recommendations."""
    payload = {
        "budget": 800000,
        "business_category": "Food",
        "location": "Bengaluru",
        "experience_years": 2,
        "expected_roi": 25,
        "risk_preference": "Low",
    }
    response = await client.post("/api/v1/recommendations/franchises", json=payload, headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()

    assert "recommendations" in data
    recs = data["recommendations"]
    assert len(recs) == 5

    # Check Top #1 Match properties
    top1 = recs[0]
    assert top1["ranking_position"] == 1
    assert 0 <= top1["match_score"] <= 100
    assert "explanation" in top1
    assert len(top1["explanation"]) > 0


@pytest.mark.asyncio
async def test_startup_recommendations_and_history(client: AsyncClient, user_token_headers: dict):
    """Test generating, retrieving, and refreshing recommendations for a startup idea."""
    # 1. Create a startup idea
    st_payload = {
        "business_name": "Cafe Express",
        "business_category": "Food",
        "business_model": "Cafe",
        "investment_amount": 600000,
        "expected_monthly_revenue": 200000,
        "expected_monthly_expenses": 120000,
        "location": "Bengaluru",
        "target_customer": "Students",
    }
    res_st = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    assert res_st.status_code == 201
    startup_id = res_st.json()["startup_id"]

    # 2. Get latest recommendations
    res_rec = await client.get(f"/api/v1/recommendations/franchises/{startup_id}", headers=user_token_headers)
    assert res_rec.status_code == 200
    data = res_rec.json()
    assert data["startup_id"] == startup_id
    assert len(data["recommendations"]) == 5

    # 3. Refresh recommendations
    res_ref = await client.post(f"/api/v1/recommendations/franchises/{startup_id}/refresh", headers=user_token_headers)
    assert res_ref.status_code == 200
    assert len(res_ref.json()["recommendations"]) == 5


@pytest.mark.asyncio
async def test_compare_franchises(client: AsyncClient):
    """Test side-by-side comparison endpoint for 2 franchises."""
    res_list = await client.get("/api/v1/franchises")
    franchises = res_list.json()
    fid1 = franchises[0]["id"]
    fid2 = franchises[1]["id"]

    comp_payload = {"franchise_ids": [fid1, fid2]}
    response = await client.post("/api/v1/franchises/compare", json=comp_payload)
    assert response.status_code == 200
    data = response.json()

    assert len(data["franchises"]) == 2
    assert "comparison_matrix" in data
    assert "investment_range" in data["comparison_matrix"]


@pytest.mark.asyncio
async def test_recommendations_forbidden_access(
    client: AsyncClient,
    user_token_headers: dict
):
    """User B cannot access recommendations for User A's startup."""
    # 1. User A creates startup prediction
    st_payload = {
        "business_name": "User A Startup",
        "business_category": "Retail",
        "investment_amount": 500000,
        "expected_monthly_revenue": 150000,
        "expected_monthly_expenses": 90000,
        "location": "Mumbai",
        "target_customer": "Shoppers",
    }
    res_a = await client.post("/api/v1/predictions/analyze", json=st_payload, headers=user_token_headers)
    startup_id = res_a.json()["startup_id"]

    # 2. Register & login User B
    email_b = f"userB_rec_{uuid4().hex[:6]}@example.com"
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

    # User B requests User A's startup recommendations -> 403 Forbidden
    res_forb = await client.get(f"/api/v1/recommendations/franchises/{startup_id}", headers=headers_b)
    assert res_forb.status_code == 403
