"""
STARTWISE AI — Marketing Strategy Repository
Data access layer for MarketingStrategy templates.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import MarketingStrategy
from app.repositories.base_repository import BaseRepository


class MarketingRepository(BaseRepository[MarketingStrategy]):
    def __init__(self, db: AsyncSession):
        super().__init__(MarketingStrategy, db)

    async def get_by_category(self, business_category: str) -> List[MarketingStrategy]:
        stmt = (
            select(MarketingStrategy)
            .where(MarketingStrategy.business_category.ilike(business_category.strip()))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_platform(self, platform: str) -> List[MarketingStrategy]:
        stmt = (
            select(MarketingStrategy)
            .where(MarketingStrategy.platform.ilike(platform.strip()))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
