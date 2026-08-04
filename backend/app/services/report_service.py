"""
STARTWISE AI — Report Service
High-level service managing report records and PDF file references.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Report
from app.repositories.report_repository import ReportRepository
from app.schemas.schemas import ReportOut, ReportCreate
from app.core.exceptions import NotFoundException
from app.database.mixins import PaginationParams, PaginatedResult


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReportRepository(db)

    async def create_report_record(self, user_id: UUID, payload: ReportCreate) -> ReportOut:
        report = await self.repo.create(
            user_id=user_id,
            startup_id=payload.startup_id,
            title=payload.title,
            pdf_path=payload.pdf_path,
            report_data=payload.report_data,
        )
        return ReportOut.model_validate(report)

    async def get_user_reports(self, user_id: UUID, page: int = 1, per_page: int = 20) -> PaginatedResult[ReportOut]:
        params = PaginationParams(page=page, per_page=per_page)
        reports = await self.repo.get_by_user_id(user_id, params=params)
        total = await self.repo.count(Report.user_id == user_id)
        outs = [ReportOut.model_validate(r) for r in reports]
        return PaginatedResult.create(items=outs, total=total, params=params)
