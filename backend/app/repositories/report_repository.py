"""
STARTWISE AI — Report Repository
Data access layer for generated Report records.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Report
from app.repositories.base_repository import BaseRepository
from app.database.mixins import PaginationParams, PaginatedResult


class ReportRepository(BaseRepository[Report]):
    def __init__(self, db: AsyncSession):
        super().__init__(Report, db)

    async def get_by_user_id(
        self, user_id: str | UUID, params: Optional[PaginationParams] = None
    ) -> List[Report]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(Report.generated_at.desc())
        )
        if params:
            stmt = stmt.offset(params.offset).limit(params.per_page)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
