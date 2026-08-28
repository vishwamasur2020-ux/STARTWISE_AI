"""
STARTWISE AI — Explainable AI (XAI) API Endpoints (Stage 13)
REST endpoints providing SHAP-based feature attribution and human-readable insights:
  - GET /api/v1/explainability/{prediction_id}             — Full combined XAI decision insights
  - GET /api/v1/explainability/success/{prediction_id}     — Success probability model explanation
  - GET /api/v1/explainability/risk/{prediction_id}        — Risk level classification explanation
  - GET /api/v1/explainability/roi/{prediction_id}         — Estimated ROI regression explanation
  - GET /api/v1/explainability/competition/{prediction_id} — Market competition density explanation
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.services.explainability_service import ExplainabilityService
from app.schemas.explainability_schemas import (
    CombinedExplanationResponse,
    SingleModelExplanationResponse,
)

router = APIRouter(prefix="/explainability", tags=["Explainable AI (XAI)"])


@router.get(
    "/{prediction_id}",
    response_model=CombinedExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Combined XAI Decision Insights",
    description="Retrieve comprehensive multi-model SHAP attribution, top positive/negative drivers, and narrative summaries.",
)
async def get_combined_explanation(
    prediction_id: UUID = Path(..., description="UUID of the PredictionResult"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated Explainable AI decision overview for a prediction."""
    service = ExplainabilityService(db)
    return await service.get_combined_explanation(prediction_id, current_user)


@router.get(
    "/success/{prediction_id}",
    response_model=SingleModelExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Success Probability Model Explanation",
    description="Inspect SHAP TreeExplainer feature attributions for the binary success prediction model.",
)
async def get_success_explanation(
    prediction_id: UUID = Path(..., description="UUID of the PredictionResult"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return SHAP explanation for the success probability model."""
    service = ExplainabilityService(db)
    return await service.get_or_calculate_explanation(prediction_id, "success", current_user)


@router.get(
    "/risk/{prediction_id}",
    response_model=SingleModelExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Risk Level Model Explanation",
    description="Inspect SHAP TreeExplainer feature attributions and risk mitigation drivers.",
)
async def get_risk_explanation(
    prediction_id: UUID = Path(..., description="UUID of the PredictionResult"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return SHAP explanation for the risk level classification model."""
    service = ExplainabilityService(db)
    return await service.get_or_calculate_explanation(prediction_id, "risk", current_user)


@router.get(
    "/roi/{prediction_id}",
    response_model=SingleModelExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Estimated ROI Model Explanation",
    description="Inspect SHAP LinearExplainer feature attributions for annual return on investment.",
)
async def get_roi_explanation(
    prediction_id: UUID = Path(..., description="UUID of the PredictionResult"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return SHAP explanation for the estimated ROI regression model."""
    service = ExplainabilityService(db)
    return await service.get_or_calculate_explanation(prediction_id, "roi", current_user)


@router.get(
    "/competition/{prediction_id}",
    response_model=SingleModelExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Competition Level Model Explanation",
    description="Inspect SHAP TreeExplainer feature attributions for market density classification.",
)
async def get_competition_explanation(
    prediction_id: UUID = Path(..., description="UUID of the PredictionResult"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return SHAP explanation for the market competition model."""
    service = ExplainabilityService(db)
    return await service.get_or_calculate_explanation(prediction_id, "competition", current_user)
