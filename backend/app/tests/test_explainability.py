"""
STARTWISE AI — Explainable AI (XAI) Test Suite (Stage 13)
Unit & integration tests verifying SHAP TreeExplainer, LinearExplainer,
feature attributions, authorization boundaries, and explanation persistence.
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from httpx import AsyncClient

from app.models.models import User, UserRole, StartupIdea, PredictionResult


@pytest_asyncio.fixture
async def startup_and_prediction(db_session, test_user):
    """Create a test startup idea and prediction result in DB."""
    startup = StartupIdea(
        user_id=test_user.id,
        business_name="NeuralEdge AI Solutions",
        business_category="Technology",
        business_model="B2B SaaS",
        investment_amount=1500000.0,
        preferred_location="Bengaluru",
        target_customers="Enterprise Tech",
        experience_years=5,
        expected_monthly_revenue=400000.0,
        market_demand=8,
        competition_level="Medium",
        employee_count=6,
        description="AI-driven enterprise workflow optimization platform.",
    )
    db_session.add(startup)
    await db_session.commit()
    await db_session.refresh(startup)

    pred = PredictionResult(
        startup_id=startup.id,
        success_probability=82.5,
        business_score=85.0,
        risk_level="Low",
        estimated_roi=38.5,
        competition_score=55.0,
        confidence_score=90.0,
        ai_recommendation={
            "score_label": "Good",
            "competition_level": "Medium",
        },
    )
    db_session.add(pred)
    await db_session.commit()
    await db_session.refresh(pred)
    return startup, pred


@pytest.mark.asyncio
async def test_xai_unauthorized(client: AsyncClient, startup_and_prediction):
    """Accessing XAI endpoint without auth token returns 401."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/{pred.id}")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_xai_cross_user_forbidden(client: AsyncClient, db_session, startup_and_prediction):
    """User B cannot access XAI explanation for User A's prediction (returns 403)."""
    _, pred = startup_and_prediction

    # Create User B
    user_b = User(
        full_name="User B",
        email=f"user_b_{uuid4().hex[:6]}@startwise.ai",
        hashed_password="$2b$12$eImiTXuWVxfM37uY4JANjO5E/XfR0hN5D1K6yF5Q3uGZ7v9u8",
        role=UserRole.user,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user_b)
    await db_session.commit()

    from app.core.security import create_access_token
    token_b = create_access_token(subject=str(user_b.id))
    headers_b = {"Authorization": f"Bearer {token_b}"}

    resp = await client.get(f"/api/v1/explainability/{pred.id}", headers=headers_b)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_success_explanation(client: AsyncClient, user_token_headers: dict, startup_and_prediction):
    """Verify SHAP TreeExplainer outputs for binary success model."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/success/{pred.id}", headers=user_token_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["model_name"] == "success"
    assert "TreeExplainer" in data["model_info"]["explanation_method"]
    assert isinstance(data["feature_contributions"], list)
    assert len(data["feature_contributions"]) > 0

    # Verify SHAP value structure
    first_feat = data["feature_contributions"][0]
    assert "display_name" in first_feat
    assert isinstance(first_feat["impact_value"], float)
    assert first_feat["direction"] in ["positive", "negative", "neutral"]

    # Verify top positive/negative factors
    assert "top_positive_factors" in data
    assert "top_negative_factors" in data
    assert "summary" in data
    assert len(data["summary"]) > 10


@pytest.mark.asyncio
async def test_risk_explanation(client: AsyncClient, user_token_headers: dict, startup_and_prediction):
    """Verify SHAP explanation for risk level classification."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/risk/{pred.id}", headers=user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "risk"
    assert data["predicted_value"] == "Low"
    assert isinstance(data["feature_contributions"], list)


@pytest.mark.asyncio
async def test_roi_explanation(client: AsyncClient, user_token_headers: dict, startup_and_prediction):
    """Verify SHAP LinearExplainer for continuous ROI model."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/roi/{pred.id}", headers=user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "roi"
    assert "LinearExplainer" in data["model_info"]["explanation_method"]
    assert isinstance(data["predicted_value"], float)


@pytest.mark.asyncio
async def test_competition_explanation(client: AsyncClient, user_token_headers: dict, startup_and_prediction):
    """Verify SHAP explanation for competition classification."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/competition/{pred.id}", headers=user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_name"] == "competition"
    assert isinstance(data["feature_contributions"], list)


@pytest.mark.asyncio
async def test_combined_explanation_and_caching(client: AsyncClient, user_token_headers: dict, startup_and_prediction):
    """Verify combined multi-model XAI summary and database explanation caching."""
    startup, pred = startup_and_prediction

    # First request: computes SHAP and caches
    resp1 = await client.get(f"/api/v1/explainability/{pred.id}", headers=user_token_headers)
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert data1["business_name"] == "NeuralEdge AI Solutions"
    assert "success" in data1
    assert "risk" in data1
    assert "roi" in data1
    assert "competition" in data1
    assert "overall_decision_summary" in data1
    assert len(data1["pipeline_steps"]) == 5

    # Second request: served from cache seamlessly
    resp2 = await client.get(f"/api/v1/explainability/{pred.id}", headers=user_token_headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["overall_decision_summary"] == data1["overall_decision_summary"]


@pytest.mark.asyncio
async def test_admin_can_access_any_explanation(client: AsyncClient, admin_token_headers: dict, startup_and_prediction):
    """Admin role can inspect XAI explanation for any user's prediction."""
    _, pred = startup_and_prediction
    resp = await client.get(f"/api/v1/explainability/{pred.id}", headers=admin_token_headers)
    assert resp.status_code == 200
    assert resp.json()["prediction_id"] == str(pred.id)
