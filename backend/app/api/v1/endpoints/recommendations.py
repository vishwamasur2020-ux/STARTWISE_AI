"""
STARTWISE AI — Recommendations Endpoints (Stage 8)

REST API endpoints for AI Franchise Recommendation Engine:
  - POST /api/v1/recommendations/franchises               — Generate personalized recommendations
  - GET  /api/v1/recommendations/franchises/{startup_id}   — Retrieve latest recommendations for startup
  - POST /api/v1/recommendations/franchises/{startup_id}/refresh — Recalculate recommendations
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.schemas.franchise_schemas import (
    FranchiseRecommendationRequest,
    FranchiseRecommendationResponse,
)
from app.services.franchise_service import FranchiseService

router = APIRouter(prefix="/recommendations", tags=["Franchise Recommendation Engine"])


@router.post(
    "/franchises",
    response_model=FranchiseRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Personalized Franchise Recommendations",
    description="Runs hybrid AI recommendation engine (NearestNeighbors + Hard Filtering + Stage 7 Signals) and returns ranked Top 5 matched franchises with explanations."
)
async def generate_recommendations(
    payload: FranchiseRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate personalized hybrid AI franchise recommendations."""
    service = FranchiseService(db)
    return await service.generate_recommendations(req=payload, current_user=current_user)


@router.get(
    "/franchises/{startup_id}",
    response_model=FranchiseRecommendationResponse,
    summary="Get Latest Franchise Recommendations for Startup",
    description="Retrieve the most recent recommendation run for a specific startup idea."
)
async def get_latest_recommendations(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve latest franchise recommendations for user's startup."""
    service = FranchiseService(db)
    return await service.get_latest_recommendations(startup_id=startup_id, current_user=current_user)


@router.post(
    "/franchises/{startup_id}/refresh",
    response_model=FranchiseRecommendationResponse,
    summary="Recalculate Franchise Recommendations",
    description="Re-runs hybrid recommendation engine using current startup idea parameters and creates new recommendation history entries."
)
async def refresh_recommendations(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recalculate franchise recommendations for startup."""
    service = FranchiseService(db)
    return await service.refresh_recommendations(startup_id=startup_id, current_user=current_user)
