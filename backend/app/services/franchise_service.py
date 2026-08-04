"""
STARTWISE AI — Franchise Service
High-level service managing franchise database search, budget filtering, and recommendation matching.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.franchise_repository import FranchiseRepository
from app.schemas.schemas import FranchiseOut, FranchiseFilterParams
from app.database.mixins import PaginationParams, PaginatedResult
from app.core.exceptions import NotFoundException


class FranchiseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FranchiseRepository(db)

    async def get_franchise_by_id(self, franchise_id: str | UUID) -> FranchiseOut:
        item = await self.repo.get_by_id(franchise_id)
        if not item or not item.is_active:
            raise NotFoundException("Franchise not found or inactive.")
        return FranchiseOut.model_validate(item)

    async def filter_franchises(
        self,
        filters: FranchiseFilterParams,
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResult[FranchiseOut]:
        params = PaginationParams(page=page, per_page=per_page)
        res = await self.repo.filter_franchises(
            category=filters.category,
            max_budget=filters.max_investment,
            min_budget=filters.min_investment,
            risk_level=filters.risk_level,
            city=filters.city,
            query=filters.query,
            params=params,
        )
        outs = [FranchiseOut.model_validate(f) for f in res.items]
        return PaginatedResult.create(items=outs, total=res.total, params=params)
