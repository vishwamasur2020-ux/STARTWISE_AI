"""
STARTWISE AI — ML Engine Health Endpoint (Stage 7)

Provides real-time health inspection of loaded Machine Learning models, preprocessors, and memory status.
"""

from fastapi import APIRouter, status
from app.core.model_manager import get_model_manager
from app.schemas.prediction_schemas import MlHealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=MlHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check ML Model Engine Health Status",
    description="Inspect whether all 4 trained joblib models and preprocessors are loaded in memory."
)
async def check_ml_health():
    """Return status of loaded ML model artifacts."""
    manager = get_model_manager()
    return manager.get_health_status()
