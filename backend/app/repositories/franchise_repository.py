"""
STARTWISE AI — Franchise Repository
Data access layer for Franchise database with filtering, search, and pagination.
"""

from typing import Optional, List
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Franchise
from app.repositories.base_repository import BaseRepository
from app.database.mixins import PaginationParams, PaginatedResult


class FranchiseRepository(BaseRepository[Franchise]):
    def __init__(self, db: AsyncSession):
        super().__init__(Franchise, db)

    async def filter_franchises(
        self,
        category: Optional[str] = None,
        max_budget: Optional[float] = None,
        min_budget: Optional[float] = None,
        risk_level: Optional[str] = None,
        city: Optional[str] = None,
        query: Optional[str] = None,
        params: Optional[PaginationParams] = None,
    ) -> PaginatedResult[Franchise]:
        conditions = [Franchise.is_active == True]

        if category:
            conditions.append(Franchise.industry.ilike(f"%{category}%"))
        if max_budget is not None:
            conditions.append(Franchise.minimum_investment <= max_budget)
        if min_budget is not None:
            conditions.append(Franchise.maximum_investment >= min_budget)
        if risk_level:
            conditions.append(Franchise.risk_level.ilike(risk_level))
        if city:
            conditions.append(Franchise.city.ilike(f"%{city}%"))
        if query:
            q = f"%{query}%"
            conditions.append(
                or_(
                    Franchise.franchise_name.ilike(q),
                    Franchise.description.ilike(q),
                    Franchise.industry.ilike(q),
                    Franchise.city.ilike(q),
                    Franchise.state.ilike(q),
                )
            )

        filter_expr = and_(*conditions)
        if params:
            return await self.paginate(params, filter_condition=filter_expr, order_by=Franchise.franchise_name.asc())

        stmt = select(Franchise).where(filter_expr).order_by(Franchise.franchise_name.asc())
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())
        total = len(items)
        dummy_params = PaginationParams(page=1, per_page=max(total, 1))
        return PaginatedResult.create(items=items, total=total, params=dummy_params)
