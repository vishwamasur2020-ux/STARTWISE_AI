"""
STARTWISE AI — Prediction Service (Stage 7)

High-level business service orchestrating ML inference, database persistence,
ownership authorization checks, and historical log retrieval.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, StartupIdea, PredictionResult
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.startup_repository import StartupRepository
from app.services.prediction_engine import PredictionEngine
from app.schemas.prediction_schemas import (
    PredictionAnalysisRequest,
    PredictionAnalysisResponse,
    SuccessPredictionOutput,
    RiskPredictionOutput,
    RoiPredictionOutput,
    CompetitionPredictionOutput,
    ModelInformationOutput,
)
from app.core.exceptions import NotFoundException, ForbiddenException


class PredictionService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pred_repo = PredictionRepository(db)
        self.startup_repo = StartupRepository(db)
        self.engine = PredictionEngine()

    async def analyze_and_save(
        self,
        payload: PredictionAnalysisRequest,
        current_user: User,
    ) -> PredictionAnalysisResponse:
        """
        Run ML analysis, ensure associated StartupIdea exists, save PredictionResult to DB,
        and return formatted API response.
        """
        startup: Optional[StartupIdea] = None

        # 1. Ownership check if startup_id provided
        if payload.startup_id:
            startup = await self.startup_repo.get_by_id(payload.startup_id)
            if not startup:
                raise NotFoundException("Startup idea not found.")
            if startup.user_id != current_user.id and current_user.role != "admin":
                raise ForbiddenException("Access denied. You can only analyze your own startup ideas.")

        # 2. Auto-create StartupIdea if no startup_id was passed
        if not startup:
            startup_data = {
                "user_id": current_user.id,
                "business_name": payload.business_name,
                "business_category": payload.business_category,
                "business_model": payload.business_model,
                "investment_amount": payload.investment_amount,
                "preferred_location": payload.location,
                "target_customers": payload.target_customer,
                "experience_years": payload.experience_years,
                "expected_monthly_revenue": payload.expected_monthly_revenue,
                "market_demand": payload.market_demand,
                "competition_level": payload.competition_level,
                "employee_count": payload.employee_count,
                "description": payload.business_description,
            }
            startup = await self.startup_repo.create(**startup_data)
            payload.startup_id = startup.id

        # 3. Run ML Inference Engine
        analysis: PredictionAnalysisResponse = self.engine.analyze(payload)
        analysis.startup_id = startup.id

        # 4. Prepare DB Persistence Payload
        db_payload = {
            "startup_id": startup.id,
            "success_probability": float(analysis.success.probability),
            "business_score": float(analysis.business_score),
            "risk_level": str(analysis.risk.level),
            "estimated_roi": float(analysis.roi.estimated_percentage),
            "competition_score": float(analysis.competition.probability),
            "confidence_score": 88.5,
            "ai_recommendation": {
                "recommendations": analysis.recommendations,
                "score_label": analysis.score_label,
                "top_features": [f.model_dump() for f in analysis.top_features],
                "model_info": analysis.model_information.model_dump(),
                "success_prediction": analysis.success.prediction,
                "risk_probability": analysis.risk.probability,
                "competition_level": analysis.competition.level,
            },
        }

        # Create new prediction history record in DB
        created_record = await self.pred_repo.create(**db_payload)
        analysis.id = created_record.id
        analysis.created_at = created_record.created_at

        return analysis

    async def get_latest_prediction(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> PredictionAnalysisResponse:
        """
        Get the most recent prediction for a startup idea with authorization check.
        """
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only access predictions for your own startups.")

        record = await self.pred_repo.get_latest_by_startup_id(startup_id)
        if not record:
            raise NotFoundException("No prediction records found for this startup. Run analysis first.")

        return self._record_to_response(record, startup)

    async def get_prediction_history(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> List[PredictionAnalysisResponse]:
        """
        Get full history of prediction records for a startup idea.
        """
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only access prediction history for your own startups.")

        records = await self.pred_repo.get_history_by_startup_id(startup_id)
        return [self._record_to_response(rec, startup) for rec in records]

    async def reanalyze_startup(
        self,
        startup_id: UUID,
        current_user: User,
    ) -> PredictionAnalysisResponse:
        """
        Re-run ML analysis on startup's current parameters in database.
        """
        startup = await self.startup_repo.get_by_id(startup_id)
        if not startup:
            raise NotFoundException("Startup idea not found.")
        if startup.user_id != current_user.id and current_user.role != "admin":
            raise ForbiddenException("Access denied. You can only re-analyze your own startup ideas.")

        req = PredictionAnalysisRequest(
            startup_id=startup.id,
            business_name=startup.business_name,
            business_category=startup.business_category,
            business_model=startup.business_model,
            business_description=startup.description,
            investment_amount=startup.investment_amount,
            expected_monthly_revenue=startup.expected_monthly_revenue,
            expected_monthly_expenses=getattr(startup, "expected_monthly_expenses", startup.investment_amount * 0.1),
            employee_count=startup.employee_count,
            experience_years=startup.experience_years,
            location=startup.preferred_location,
            target_customer=startup.target_customers,
            market_demand=startup.market_demand,
            competition_level=startup.competition_level,
        )

        return await self.analyze_and_save(req, current_user)

    def _record_to_response(
        self,
        rec: PredictionResult,
        startup: StartupIdea,
    ) -> PredictionAnalysisResponse:
        """Convert ORM PredictionResult to structured response object."""
        rec_data = rec.ai_recommendation or {}
        recommendations = rec_data.get("recommendations", [])
        score_label = rec_data.get("score_label", "Good")
        success_pred = rec_data.get("success_prediction", rec.success_probability >= 50.0)
        risk_prob = rec_data.get("risk_probability", 80.0)
        comp_level = rec_data.get("competition_level", startup.competition_level)
        top_feats = rec_data.get("top_features", [])

        return PredictionAnalysisResponse(
            id=rec.id,
            startup_id=rec.startup_id,
            business_name=startup.business_name,
            success=SuccessPredictionOutput(
                prediction=success_pred,
                probability=rec.success_probability,
            ),
            risk=RiskPredictionOutput(
                level=rec.risk_level,
                probability=risk_prob,
            ),
            roi=RoiPredictionOutput(
                estimated_percentage=rec.estimated_roi,
            ),
            competition=CompetitionPredictionOutput(
                level=comp_level,
                probability=rec.competition_score,
            ),
            business_score=rec.business_score,
            score_label=score_label,
            recommendations=recommendations,
            model_information=ModelInformationOutput(),
            top_features=top_feats,
            created_at=rec.created_at,
        )
