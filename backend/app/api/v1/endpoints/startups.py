"""
STARTWISE AI — Startup Endpoints (Stage 5 API Router)
REST API endpoints for Startup Validation Module: CRUD, recent items, and user statistics.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.models import User
from app.schemas.schemas import (
    StartupIdeaCreate,
    StartupIdeaUpdate,
    StartupIdeaOut,
    MessageResponse,
)
from app.database.mixins import PaginatedResult
from app.services.startup_service import StartupService

router = APIRouter()


@router.post("", response_model=StartupIdeaOut, status_code=status.HTTP_201_CREATED)
async def create_startup(
    payload: StartupIdeaCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new startup idea for validation."""
    service = StartupService(db)
    return await service.create_startup_idea(user_id=current_user.id, payload=payload)


@router.get("", response_model=PaginatedResult[StartupIdeaOut])
async def list_startups(
    query: Optional[str] = Query(None, description="Search by name, description, location"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    min_investment: Optional[float] = Query(None, ge=0, description="Minimum investment filter"),
    max_investment: Optional[float] = Query(None, ge=0, description="Maximum investment filter"),
    sort_by: str = Query("newest", description="Sorting: newest, oldest, highest_investment, lowest_investment, alphabetical"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List authenticated user's startup ideas with search, category/investment filters, sorting, and pagination."""
    service = StartupService(db)
    return await service.filter_user_ideas(
        user_id=current_user.id,
        query=query,
        category=category,
        min_investment=min_investment,
        max_investment=max_investment,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
    )


@router.get("/recent", response_model=List[StartupIdeaOut])
async def get_recent_startups(
    limit: int = Query(5, ge=1, le=20, description="Number of recent startups to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve 5 most recent startup ideas for the authenticated user's dashboard."""
    service = StartupService(db)
    return await service.get_recent_startups(user_id=current_user.id, limit=limit)


@router.get("/statistics", response_model=Dict[str, Any])
async def get_startup_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve dashboard statistics summary for the authenticated user."""
    service = StartupService(db)
    return await service.get_startup_statistics(user_id=current_user.id)


@router.get("/{id}", response_model=StartupIdeaOut)
async def get_startup_details(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed startup idea information by ID."""
    service = StartupService(db)
    return await service.get_idea_by_id(idea_id=id, user_id=current_user.id)


@router.put("/{id}", response_model=StartupIdeaOut)
async def update_startup(
    id: UUID,
    payload: StartupIdeaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing startup idea."""
    service = StartupService(db)
    return await service.update_startup_idea(idea_id=id, user_id=current_user.id, payload=payload)


@router.delete("/{id}", response_model=MessageResponse)
async def delete_startup(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a startup idea."""
    service = StartupService(db)
    await service.delete_user_idea(idea_id=id, user_id=current_user.id)
    return MessageResponse(message="Startup idea deleted successfully.", success=True)
