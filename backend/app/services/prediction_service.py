"""
STARTWISE AI — Prediction Service
High-level service managing AI prediction result records and associations.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PredictionResult
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.schemas import PredictionResultCreate, PredictionResultOut
from app.core.exceptions import NotFoundException


class PredictionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PredictionRepository(db)

    async def save_prediction(self, payload: PredictionResultCreate) -> PredictionResultOut:
        data = payload.model_dump()

        # Check existing prediction for startup_id
        existing = await self.repo.get_by_startup_id(payload.startup_id)
        if existing:
            updated = await self.repo.update(existing, **data)
            return PredictionResultOut.model_validate(updated)

        created = await self.repo.create(**data)
        return PredictionResultOut.model_validate(created)

    async def get_prediction_by_startup_id(self, startup_id: str | UUID) -> PredictionResultOut:
        result = await self.repo.get_by_startup_id(startup_id)
        if not result:
            raise NotFoundException("Prediction result not found for this startup idea.")
        return PredictionResultOut.model_validate(result)
