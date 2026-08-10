"""
STARTWISE AI -- Dashboard API Endpoints (Stage 10)
Aggregated routes for AI Business Intelligence Dashboard (/api/v1/dashboard).
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schemas import (
    DashboardResponse,
    DashboardStatisticsResponse,
    AnalysisComparisonRequest,
    AnalysisComparisonResponse,
    ActivityItem,
    NotificationItem,
)

router = APIRouter()

@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve aggregated dashboard information for current user's default/latest startup."""
    service = DashboardService(db)
    return await service.get_user_dashboard(user_id=current_user.id)

@router.get("/startups/{startup_id}", response_model=DashboardResponse)
async def get_startup_dashboard(
    startup_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve aggregated dashboard information for a specific startup idea."""
    service = DashboardService(db)
    try:
        return await service.get_user_dashboard(user_id=current_user.id, startup_id=startup_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/statistics", response_model=DashboardStatisticsResponse)
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve overall user startup platform statistics."""
    service = DashboardService(db)
    return await service.get_dashboard_statistics(user_id=current_user.id)

@router.post("/compare", response_model=AnalysisComparisonResponse)
async def compare_analyses(
    req: AnalysisComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compare two prediction analyses side-by-side."""
    service = DashboardService(db)
    try:
        return await service.compare_analyses(
            user_id=current_user.id, id_a=req.analysis_id_a, id_b=req.analysis_id_b
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/activities", response_model=List[ActivityItem])
async def get_recent_activities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve user recent activity log."""
    service = DashboardService(db)
    dash = await service.get_user_dashboard(user_id=current_user.id)
    return dash.activities

@router.get("/notifications", response_model=List[NotificationItem])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve user notification feed."""
    service = DashboardService(db)
    dash = await service.get_user_dashboard(user_id=current_user.id)
    return dash.notifications
