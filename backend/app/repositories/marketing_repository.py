"""
STARTWISE AI — Marketing Repository (Stage 9)

Data access layer for MarketingStrategy model.
Stores and retrieves marketing strategy analysis records per startup idea.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import MarketingStrategy
from app.repositories.base_repository import BaseRepository


class MarketingRepository(BaseRepository[MarketingStrategy]):

    def __init__(self, db: AsyncSession):
        super().__init__(MarketingStrategy, db)

    async def get_latest_by_startup_id(self, startup_id: UUID) -> Optional[MarketingStrategy]:
        """Fetch the most recent marketing strategy record for a startup idea."""
        stmt = (
            select(MarketingStrategy)
            .where(MarketingStrategy.startup_id == startup_id)
            .order_by(MarketingStrategy.created_at.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_history_by_startup_id(self, startup_id: UUID) -> List[MarketingStrategy]:
        """Fetch all marketing strategy history entries for a startup idea."""
        stmt = (
            select(MarketingStrategy)
            .where(MarketingStrategy.startup_id == startup_id)
            .order_by(MarketingStrategy.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
