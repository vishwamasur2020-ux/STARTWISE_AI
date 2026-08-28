"""
STARTWISE AI — Explainability Repository (Stage 13)
Data access layer for cached prediction explanations (SHAP values & factor insights).
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PredictionExplanation, PredictionResult


class ExplainabilityRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_prediction_and_model(
        self,
        prediction_id: UUID,
        model_name: str,
    ) -> Optional[PredictionExplanation]:
        """Fetch cached explanation for a specific prediction and model."""
        stmt = (
            select(PredictionExplanation)
            .where(
                and_(
                    PredictionExplanation.prediction_id == prediction_id,
                    PredictionExplanation.model_name == model_name,
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_all_by_prediction(
        self,
        prediction_id: UUID,
    ) -> List[PredictionExplanation]:
        """Fetch all cached model explanations for a prediction."""
        stmt = (
            select(PredictionExplanation)
            .where(PredictionExplanation.prediction_id == prediction_id)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def save_explanation(
        self,
        prediction_id: UUID,
        model_name: str,
        explanation_method: str,
        feature_contributions: List[Dict[str, Any]],
        positive_factors: List[Dict[str, Any]],
        negative_factors: List[Dict[str, Any]],
        summary: Any,
        model_version: str = "1.0.0",
        explanation_version: str = "1.0.0",
    ) -> PredictionExplanation:
        """Create or update cached explanation record."""
        existing = await self.get_by_prediction_and_model(prediction_id, model_name)
        if existing:
            existing.explanation_method = explanation_method
            existing.feature_contributions = feature_contributions
            existing.positive_factors = positive_factors
            existing.negative_factors = negative_factors
            existing.summary = summary
            existing.model_version = model_version
            existing.explanation_version = explanation_version
            existing.created_at = datetime.now(timezone.utc)
            await self.db.flush()
            return existing

        explanation = PredictionExplanation(
            prediction_id=prediction_id,
            model_name=model_name,
            explanation_method=explanation_method,
            feature_contributions=feature_contributions,
            positive_factors=positive_factors,
            negative_factors=negative_factors,
            summary=summary,
            model_version=model_version,
            explanation_version=explanation_version,
        )
        self.db.add(explanation)
        await self.db.flush()
        return explanation

    async def delete_by_prediction(self, prediction_id: UUID) -> None:
        """Delete all cached explanations for a prediction."""
        stmt = delete(PredictionExplanation).where(
            PredictionExplanation.prediction_id == prediction_id
        )
        await self.db.execute(stmt)
