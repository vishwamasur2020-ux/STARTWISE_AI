"""
STARTWISE AI — Prediction Repository
Data access layer for PredictionResult model supporting latest predictions and historical logs.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PredictionResult
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[PredictionResult]):
    def __init__(self, db: AsyncSession):
        super().__init__(PredictionResult, db)

    async def get_latest_by_startup_id(self, startup_id: str | UUID) -> Optional[PredictionResult]:
        """Get the most recent prediction result for a startup idea."""
        if isinstance(startup_id, str):
            startup_id = UUID(startup_id)
        stmt = (
            select(PredictionResult)
            .where(PredictionResult.startup_id == startup_id)
            .order_by(PredictionResult.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_startup_id(self, startup_id: str | UUID) -> Optional[PredictionResult]:
        """Alias for get_latest_by_startup_id."""
        return await self.get_latest_by_startup_id(startup_id)

    async def get_history_by_startup_id(self, startup_id: str | UUID) -> List[PredictionResult]:
        """Get full history of prediction records for a startup idea ordered newest first."""
        if isinstance(startup_id, str):
            startup_id = UUID(startup_id)
        stmt = (
            select(PredictionResult)
            .where(PredictionResult.startup_id == startup_id)
            .order_by(PredictionResult.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
