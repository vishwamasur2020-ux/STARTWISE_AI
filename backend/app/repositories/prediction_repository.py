"""
STARTWISE AI — Prediction Repository
Data access layer for PredictionResult model.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PredictionResult
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[PredictionResult]):
    def __init__(self, db: AsyncSession):
        super().__init__(PredictionResult, db)

    async def get_by_startup_id(self, startup_id: str | UUID) -> Optional[PredictionResult]:
        if isinstance(startup_id, str):
            startup_id = UUID(startup_id)
        stmt = select(PredictionResult).where(PredictionResult.startup_id == startup_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
