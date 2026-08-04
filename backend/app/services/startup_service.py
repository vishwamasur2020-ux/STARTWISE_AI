"""
STARTWISE AI — Startup Service (Stage 5 Complete)
High-level service managing startup idea CRUD operations, authorization guards, statistics, and filtering.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import StartupIdea
from app.repositories.startup_repository import StartupRepository
from app.schemas.schemas import StartupIdeaCreate, StartupIdeaUpdate, StartupIdeaOut
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.database.mixins import PaginationParams, PaginatedResult


class StartupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StartupRepository(db)

    async def create_startup_idea(self, user_id: UUID, payload: StartupIdeaCreate) -> StartupIdeaOut:
        # Check duplicate business name for the user
        existing = await self.repo.get_by_name_and_user(user_id, payload.business_name)
        if existing:
            raise BadRequestException(f"You already have a startup idea named '{payload.business_name}'.")

        data = payload.model_dump(exclude_none=True)
        # Clean up alias fields if passed in data
        for alias in ["location", "target_customer", "business_experience_years", "monthly_revenue", "market_demand_score", "employees_count"]:
            data.pop(alias, None)

        idea = await self.repo.create(user_id=user_id, **data)
        return StartupIdeaOut.model_validate(idea)

    async def get_idea_by_id(self, idea_id: str | UUID, user_id: Optional[UUID] = None) -> StartupIdeaOut:
        idea = await self.repo.get_with_prediction(idea_id)
        if not idea:
            raise NotFoundException("Startup idea not found.")
        if user_id and idea.user_id != user_id:
            raise ForbiddenException("You do not have access to view this startup idea.")
        return StartupIdeaOut.model_validate(idea)

    async def update_startup_idea(
        self, idea_id: str | UUID, user_id: UUID, payload: StartupIdeaUpdate
    ) -> StartupIdeaOut:
        idea = await self.repo.get_by_id(idea_id)
        if not idea:
            raise NotFoundException("Startup idea not found.")
        if idea.user_id != user_id:
            raise ForbiddenException("You do not have permission to update this startup idea.")

        update_data = payload.model_dump(exclude_none=True)
        updated = await self.repo.update(idea, **update_data)
        return StartupIdeaOut.model_validate(updated)

    async def delete_user_idea(self, idea_id: str | UUID, user_id: UUID) -> None:
        idea = await self.repo.get_by_id(idea_id)
        if not idea:
            raise NotFoundException("Startup idea not found.")
        if idea.user_id != user_id:
            raise ForbiddenException("You do not have permission to delete this startup idea.")
        await self.repo.delete(idea)

    async def filter_user_ideas(
        self,
        user_id: UUID,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_investment: Optional[float] = None,
        max_investment: Optional[float] = None,
        sort_by: str = "newest",
        page: int = 1,
        per_page: int = 20,
    ) -> PaginatedResult[StartupIdeaOut]:
        params = PaginationParams(page=page, per_page=per_page)
        res = await self.repo.filter_and_paginate(
            user_id=user_id,
            query=query,
            category=category,
            min_investment=min_investment,
            max_investment=max_investment,
            sort_by=sort_by,
            params=params,
        )
        outs = [StartupIdeaOut.model_validate(item) for item in res.items]
        return PaginatedResult.create(items=outs, total=res.total, params=params)

    async def get_recent_startups(self, user_id: UUID, limit: int = 5) -> List[StartupIdeaOut]:
        items = await self.repo.get_recent_by_user(user_id=user_id, limit=limit)
        return [StartupIdeaOut.model_validate(i) for i in items]

    async def get_startup_statistics(self, user_id: UUID) -> Dict[str, Any]:
        return await self.repo.get_user_statistics(user_id=user_id)
