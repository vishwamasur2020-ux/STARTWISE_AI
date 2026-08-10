"""
STARTWISE AI — Franchise Endpoints (Stage 8)

REST API endpoints for browsing, filtering, searching, and comparing franchises:
  - GET  /api/v1/franchises             — List & filter franchises
  - GET  /api/v1/franchises/categories  — Available unique industries
  - GET  /api/v1/franchises/locations   — Supported unique cities
  - POST /api/v1/franchises/compare     — Side-by-side comparison matrix
  - GET  /api/v1/franchises/{id}        — Single franchise details
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.franchise_schemas import (
    FranchiseOut,
    FranchiseComparisonRequest,
    FranchiseComparisonResponse,
)
from app.services.franchise_service import FranchiseService

router = APIRouter(prefix="/franchises", tags=["Franchises Catalog"])


@router.get(
    "",
    response_model=List[FranchiseOut],
    summary="List & Filter Franchises",
    description="Browse active franchise catalog with optional category, investment, risk, city, or keyword search filters."
)
async def list_franchises(
    category: Optional[str] = Query(None, description="Filter by business category/industry"),
    min_investment: Optional[float] = Query(None, ge=0, description="Minimum investment threshold"),
    max_investment: Optional[float] = Query(None, ge=0, description="Maximum investment threshold"),
    risk_level: Optional[str] = Query(None, description="Filter by risk rating (Low, Medium, High)"),
    city: Optional[str] = Query(None, description="Filter by city/location"),
    query: Optional[str] = Query(None, description="Keyword search in name, description, city"),
    db: AsyncSession = Depends(get_db),
):
    """List & filter franchise catalog."""
    service = FranchiseService(db)
    return await service.list_franchises(
        category=category,
        min_investment=min_investment,
        max_investment=max_investment,
        risk_level=risk_level,
        city=city,
        query=query,
    )


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get Unique Franchise Categories",
    description="Return list of distinct categories available in franchise catalog."
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Return available franchise categories."""
    service = FranchiseService(db)
    return await service.get_categories()


@router.get(
    "/locations",
    response_model=List[str],
    summary="Get Unique Franchise Locations",
    description="Return list of distinct cities available in franchise catalog."
)
async def get_locations(db: AsyncSession = Depends(get_db)):
    """Return available franchise locations."""
    service = FranchiseService(db)
    return await service.get_locations()


@router.post(
    "/compare",
    response_model=FranchiseComparisonResponse,
    summary="Compare Franchises Side-by-Side",
    description="Pass 2 to 4 franchise UUIDs to generate a structured comparison matrix."
)
async def compare_franchises(
    payload: FranchiseComparisonRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate side-by-side comparison matrix for selected franchises."""
    service = FranchiseService(db)
    return await service.compare_franchises(payload.franchise_ids)


@router.get(
    "/{id}",
    response_model=FranchiseOut,
    summary="Get Single Franchise Details",
    description="Retrieve full details for a specific franchise by ID."
)
async def get_franchise_details(
    id: UUID = Path(..., description="UUID of the franchise"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve single franchise details."""
    service = FranchiseService(db)
    return await service.get_franchise_by_id(id)
