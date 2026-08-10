"""
STARTWISE AI — Franchise Recommendation Repository (Stage 8)

Data access layer for FranchiseRecommendation ORM model.
Stores and retrieves historical recommendation runs per startup idea.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import FranchiseRecommendation
from app.repositories.base_repository import BaseRepository


class FranchiseRecommendationRepository(BaseRepository[FranchiseRecommendation]):

    def __init__(self, db: AsyncSession):
        super().__init__(FranchiseRecommendation, db)

    async def get_latest_by_startup_id(self, startup_id: UUID) -> List[FranchiseRecommendation]:
        """Fetch the most recent recommendation run items for a startup idea."""
        stmt = (
            select(FranchiseRecommendation)
            .where(FranchiseRecommendation.startup_id == startup_id)
            .options(selectinload(FranchiseRecommendation.franchise))
            .order_by(FranchiseRecommendation.created_at.desc(), FranchiseRecommendation.ranking_position.asc())
        )
        res = await self.db.execute(stmt)
        all_recs = list(res.scalars().all())

        if not all_recs:
            return []

        # Find latest created_at timestamp
        latest_ts = all_recs[0].created_at
        latest_items = [r for r in all_recs if r.created_at == latest_ts]
        latest_items.sort(key=lambda r: r.ranking_position)
        return latest_items

    async def get_history_by_startup_id(self, startup_id: UUID) -> List[FranchiseRecommendation]:
        """Fetch full historical recommendation records for a startup idea."""
        stmt = (
            select(FranchiseRecommendation)
            .where(FranchiseRecommendation.startup_id == startup_id)
            .options(selectinload(FranchiseRecommendation.franchise))
            .order_by(FranchiseRecommendation.created_at.desc(), FranchiseRecommendation.ranking_position.asc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
