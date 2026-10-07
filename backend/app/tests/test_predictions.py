"""
STARTWISE AI — Prediction API Test Suite (Stage 7)

Comprehensive backend pytest suite for Stage 7 AI Prediction Engine:
  - ML Engine health status endpoint
  - Successful prediction analysis & database persistence
  - Pydantic input validations (negative values, empty strings)
  - Security & Authorization rules (401 Unauthorized, 403 Forbidden cross-user access)
  - History log retrieval
  - Reanalysis execution
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_ml_health_endpoint(client: AsyncClient):
    """Verify /api/v1/ml/health endpoint returns model health status."""
    response = await client.get("/api/v1/ml/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "models_loaded" in data
    assert "models" in data
    assert data["models"]["success"] is True
    assert data["models"]["risk"] is True
    assert data["models"]["roi"] is True
    assert data["models"]["competition"] is True


@pytest.mark.asyncio
async def test_prediction_analyze_unauthorized(client: AsyncClient):
    """Analyze endpoint requires authentication token."""
    payload = {
        "business_name": "Test Startup",
        "business_category": "Food",
        "business_model": "Cafe",
        "investment_amount": 500000,
        "expected_monthly_revenue": 150000,
        "expected_monthly_expenses": 90000,
        "employee_count": 4,
        "experience_years": 3,
        "location": "Bengaluru",
        "target_customer": "Students",
        "market_demand": 7,
    }
    response = await client.post("/api/v1/predictions/analyze", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_prediction_input_validation_negative_investment(client: AsyncClient, user_token_headers: dict):
    """Investment amount must be > 0."""
    payload = {
        "business_name": "Invalid Startup",
        "business_category": "Food",
        "investment_amount": -50000,  # Invalid
        "expected_monthly_revenue": 150000,
        "expected_monthly_expenses": 90000,
        "location": "Bengaluru",
        "target_customer": "Students",
    }
    response = await client.post("/api/v1/predictions/analyze", json=payload, headers=user_token_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_prediction_input_validation_empty_name(client: AsyncClient, user_token_headers: dict):
    """Business name cannot be empty."""
    payload = {
        "business_name": " ",  # Invalid
        "business_category": "Food",
        "investment_amount": 500000,
        "expected_monthly_revenue": 150000,
        "expected_monthly_expenses": 90000,
        "location": "Bengaluru",
        "target_customer": "Students",
    }
    response = await client.post("/api/v1/predictions/analyze", json=payload, headers=user_token_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_prediction_analyze_success(client: AsyncClient, user_token_headers: dict):
    """Successful prediction analysis with valid payload."""
    payload = {
        "business_name": "Urban Brew Lounge",
        "business_category": "Food",
        "business_model": "Cafe",
        "business_description": "Specialty coffee workstation with high-speed internet",
        "investment_amount": 800000,
        "expected_monthly_revenue": 250000,
        "expected_monthly_expenses": 150000,
        "employee_count": 5,
        "experience_years": 4,
        "location": "Bengaluru",
        "target_customer": "Tech professionals & students",
        "market_demand": 8,
        "competition_level": "Medium",
        "funding_source": "Personal",
    }
    response = await client.post("/api/v1/predictions/analyze", json=payload, headers=user_token_headers)
    assert response.status_code == 201
    data = response.json()

    assert "startup_id" in data
    assert data["business_name"] == "Urban Brew Lounge"
    assert 0 <= data["success"]["probability"] <= 100
    assert data["risk"]["level"] in ("Low", "Medium", "High")
    assert isinstance(data["roi"]["estimated_percentage"], float)
    assert data["competition"]["level"] in ("Low", "Medium", "High")
    assert 0 <= data["business_score"] <= 100
    assert data["score_label"] in ("Excellent", "Good", "Moderate", "High Risk", "Very High Risk")
    assert len(data["recommendations"]) > 0
    assert data["model_information"]["success_model"] == "RandomForestClassifier"


@pytest.mark.asyncio
async def test_get_latest_prediction_and_history(client: AsyncClient, user_token_headers: dict):
    """Test retrieving latest prediction and prediction history logs."""
    # 1. Create a startup & prediction
    payload = {
        "business_name": "Tech SaaS Solutions",
        "business_category": "Technology",
        "business_model": "SaaS",
        "investment_amount": 1200000,
        "expected_monthly_revenue": 350000,
        "expected_monthly_expenses": 180000,
        "employee_count": 6,
        "experience_years": 5,
        "location": "Bengaluru",
        "target_customer": "Businesses",
        "market_demand": 9,
    }
    res1 = await client.post("/api/v1/predictions/analyze", json=payload, headers=user_token_headers)
    assert res1.status_code == 201
    startup_id = res1.json()["startup_id"]

    # 2. Get latest prediction
    res_latest = await client.get(f"/api/v1/predictions/{startup_id}", headers=user_token_headers)
    assert res_latest.status_code == 200
    assert res_latest.json()["startup_id"] == startup_id

    # 3. Re-analyze to generate a second prediction record
    res_re = await client.post(f"/api/v1/predictions/{startup_id}/reanalyze", headers=user_token_headers)
    assert res_re.status_code == 200

    # 4. Get history logs
    res_hist = await client.get(f"/api/v1/predictions/{startup_id}/history", headers=user_token_headers)
    assert res_hist.status_code == 200
    history = res_hist.json()
    assert isinstance(history, list)
    assert len(history) >= 2


@pytest.mark.asyncio
async def test_cross_user_access_forbidden(
    client: AsyncClient,
    user_token_headers: dict,
    admin_token_headers: dict
):
    """User B cannot access User A's startup prediction."""
    # 1. User A creates startup prediction
    payload = {
        "business_name": "User A Startup",
        "business_category": "Retail",
        "business_model": "Store",
        "investment_amount": 600000,
        "expected_monthly_revenue": 180000,
        "expected_monthly_expenses": 100000,
        "location": "Mumbai",
        "target_customer": "General Public",
    }
    res_a = await client.post("/api/v1/predictions/analyze", json=payload, headers=user_token_headers)
    assert res_a.status_code == 201
    startup_id = res_a.json()["startup_id"]

    # 2. Register and login User B
    email_b = f"userB_{uuid4().hex[:6]}@example.com"
    pass_b = "Password123!"
    second_user_payload = {
        "full_name": "User B",
        "email": email_b,
        "password": pass_b,
        "confirm_password": pass_b,
    }
    res_reg = await client.post("/api/v1/auth/register", json=second_user_payload)
    assert res_reg.status_code == 201

    from app.database.session import AsyncSessionLocal
    from app.models.models import User
    from sqlalchemy import update
    async with AsyncSessionLocal() as session:
        await session.execute(update(User).where(User.email == email_b.lower()).values(email_verified=True, is_verified=True))
        await session.commit()

    res_login = await client.post("/api/v1/auth/login", json={"email": email_b, "password": pass_b})
    assert res_login.status_code == 200
    user_b_token = res_login.json()["access_token"]
    user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

    # User B requests User A's prediction -> 403 Forbidden
    res_forbidden = await client.get(f"/api/v1/predictions/{startup_id}", headers=user_b_headers)
    assert res_forbidden.status_code == 403
