"""
STARTWISE AI — Prediction Endpoints (Stage 7)

REST API endpoints for AI Startup Feasibility Analysis:
  - POST /api/predictions/analyze               — Run complete AI analysis
  - GET  /api/predictions/{startup_id}           — Get latest prediction
  - GET  /api/predictions/{startup_id}/history   — Get prediction history logs
  - POST /api/predictions/{startup_id}/reanalyze — Re-run analysis on startup data
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.schemas.prediction_schemas import (
    PredictionAnalysisRequest,
    PredictionAnalysisResponse,
)
from app.services.prediction_service import PredictionService

router = APIRouter()


@router.post(
    "/analyze",
    response_model=PredictionAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run Complete AI Startup Feasibility Analysis",
    description="Accepts business financial & market parameters, runs 4 ML models, calculates overall Business Score, generates dynamic recommendations, and saves prediction record to DB."
)
async def analyze_startup(
    payload: PredictionAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run AI feasibility analysis on startup concept."""
    service = PredictionService(db)
    return await service.analyze_and_save(payload=payload, current_user=current_user)


@router.get(
    "/{startup_id}",
    response_model=PredictionAnalysisResponse,
    summary="Get Latest Prediction Result",
    description="Retrieve the most recent AI feasibility analysis result for a given startup idea."
)
async def get_latest_prediction(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve latest prediction for user startup."""
    service = PredictionService(db)
    return await service.get_latest_prediction(startup_id=startup_id, current_user=current_user)


@router.get(
    "/{startup_id}/history",
    response_model=List[PredictionAnalysisResponse],
    summary="Get Prediction History Logs",
    description="Retrieve full history of past AI feasibility analysis records for a given startup idea."
)
async def get_prediction_history(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve prediction history logs for user startup."""
    service = PredictionService(db)
    return await service.get_prediction_history(startup_id=startup_id, current_user=current_user)


@router.post(
    "/{startup_id}/reanalyze",
    response_model=PredictionAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-Analyze Startup Idea",
    description="Re-runs ML models using current startup idea parameters stored in database and creates a new prediction history entry."
)
async def reanalyze_startup(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-analyze startup idea with ML engine."""
    service = PredictionService(db)
    return await service.reanalyze_startup(startup_id=startup_id, current_user=current_user)
