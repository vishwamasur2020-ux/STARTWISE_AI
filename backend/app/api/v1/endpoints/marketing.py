"""
STARTWISE AI — Marketing Endpoints (Stage 9)

REST API endpoints for AI Marketing & Promotion Strategy Engine:
  - POST /api/v1/marketing/analyze               — Generate complete marketing strategy
  - GET  /api/v1/marketing/{startup_id}            — Get latest marketing strategy
  - POST /api/v1/marketing/{startup_id}/regenerate — Regenerate strategy
  - GET  /api/v1/marketing/{startup_id}/channels   — Get recommended marketing channels
  - GET  /api/v1/marketing/{startup_id}/plan       — Get 30-day marketing plan
  - GET  /api/v1/marketing/{startup_id}/content    — Get content strategy
"""

from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.schemas.marketing_schemas import (
    MarketingStrategyRequest,
    MarketingStrategyResponse,
    MarketingChannelItem,
    ThirtyDayWeekPhase,
)
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["AI Marketing Engine"])


@router.post(
    "/analyze",
    response_model=MarketingStrategyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Personalized Marketing Strategy",
    description="Analyzes startup profile and Stage 7 ML prediction signals to generate scored channels, budget allocation, campaign ideas, 30-day plan, and KPIs."
)
async def analyze_marketing(
    payload: MarketingStrategyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate personalized AI marketing strategy."""
    service = MarketingService(db)
    return await service.analyze_and_create_strategy(req=payload, current_user=current_user)


@router.get(
    "/{startup_id}",
    response_model=MarketingStrategyResponse,
    summary="Get Latest Marketing Strategy for Startup",
    description="Retrieve the most recent marketing strategy for a specific startup idea."
)
async def get_latest_strategy(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve latest marketing strategy."""
    service = MarketingService(db)
    return await service.get_latest_strategy(startup_id=startup_id, current_user=current_user)


@router.post(
    "/{startup_id}/regenerate",
    response_model=MarketingStrategyResponse,
    summary="Regenerate Marketing Strategy",
    description="Re-runs AI Marketing Recommendation Engine using latest parameters and persists new strategy entry."
)
async def regenerate_strategy(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Regenerate marketing strategy."""
    service = MarketingService(db)
    return await service.regenerate_strategy(startup_id=startup_id, current_user=current_user)


@router.get(
    "/{startup_id}/channels",
    response_model=List[MarketingChannelItem],
    summary="Get Recommended Channels Only",
    description="Returns the Top 5 ranked and scored marketing channels for the startup."
)
async def get_recommended_channels(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return top recommended channels."""
    service = MarketingService(db)
    res = await service.get_latest_strategy(startup_id=startup_id, current_user=current_user)
    return res.recommended_channels


@router.get(
    "/{startup_id}/plan",
    response_model=List[ThirtyDayWeekPhase],
    summary="Get 30-Day Marketing Plan",
    description="Returns week-by-week timeline tasks and KPIs for 30-day execution."
)
async def get_thirty_day_plan(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return 30-day plan timeline."""
    service = MarketingService(db)
    res = await service.get_latest_strategy(startup_id=startup_id, current_user=current_user)
    return res.thirty_day_plan


@router.get(
    "/{startup_id}/content",
    response_model=Dict[str, Any],
    summary="Get Content Strategy Ideas",
    description="Returns content pillars, social posts, Reels/Shorts ideas, blog topics, and email/WhatsApp copy."
)
async def get_content_strategy(
    startup_id: UUID = Path(..., description="UUID of the startup idea"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return content strategy ideas."""
    service = MarketingService(db)
    res = await service.get_latest_strategy(startup_id=startup_id, current_user=current_user)
    return res.content_strategy
