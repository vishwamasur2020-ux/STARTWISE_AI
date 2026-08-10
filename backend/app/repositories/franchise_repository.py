"""
STARTWISE AI — Franchise Repository (Stage 8)

Data access layer for Franchise model: browsing, search, filter parameters,
categories, and locations retrieval.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Franchise
from app.repositories.base_repository import BaseRepository


class FranchiseRepository(BaseRepository[Franchise]):

    def __init__(self, db: AsyncSession):
        super().__init__(Franchise, db)

    async def get_all_active(self) -> List[Franchise]:
        """Fetch all active franchise records for recommendation engine."""
        stmt = select(Franchise).where(Franchise.is_active == True).order_by(Franchise.franchise_name.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def filter_franchises(
        self,
        category: Optional[str] = None,
        min_investment: Optional[float] = None,
        max_investment: Optional[float] = None,
        risk_level: Optional[str] = None,
        city: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[Franchise]:
        """Filter franchises by search parameters."""
        stmt = select(Franchise).where(Franchise.is_active == True)

        if category:
            stmt = stmt.where(func.lower(Franchise.industry).like(f"%{category.lower()}%"))

        if min_investment is not None:
            stmt = stmt.where(Franchise.maximum_investment >= min_investment)

        if max_investment is not None:
            stmt = stmt.where(Franchise.minimum_investment <= max_investment)

        if risk_level:
            stmt = stmt.where(func.lower(Franchise.risk_level) == risk_level.lower())

        if city:
            stmt = stmt.where(func.lower(Franchise.city).like(f"%{city.lower()}%"))

        if query:
            pattern = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Franchise.franchise_name).like(pattern),
                    func.lower(Franchise.industry).like(pattern),
                    func.lower(Franchise.description).like(pattern),
                    func.lower(Franchise.city).like(pattern),
                )
            )

        stmt = stmt.order_by(Franchise.franchise_name.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_unique_categories(self) -> List[str]:
        """Return list of distinct categories/industries."""
        stmt = select(Franchise.industry).where(Franchise.is_active == True).distinct()
        res = await self.db.execute(stmt)
        cats = [c for c in res.scalars().all() if c]
        return sorted(list(set(cats)))

    async def get_unique_locations(self) -> List[str]:
        """Return list of distinct cities/locations."""
        stmt = select(Franchise.city).where(Franchise.is_active == True, Franchise.city.isnot(None)).distinct()
        res = await self.db.execute(stmt)
        cities = [c for c in res.scalars().all() if c]
        return sorted(list(set(cities)))
