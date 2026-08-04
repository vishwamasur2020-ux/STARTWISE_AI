"""
STARTWISE AI — Startup Idea Repository (Stage 5 Complete)
Data access layer for StartupIdea model with advanced filtering, sorting, statistics, and pagination.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import StartupIdea
from app.repositories.base_repository import BaseRepository
from app.database.mixins import PaginationParams, PaginatedResult


class StartupRepository(BaseRepository[StartupIdea]):
    def __init__(self, db: AsyncSession):
        super().__init__(StartupIdea, db)

    async def get_by_user_id(
        self, user_id: str | UUID, params: Optional[PaginationParams] = None
    ) -> List[StartupIdea]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            select(StartupIdea)
            .where(StartupIdea.user_id == user_id)
            .options(selectinload(StartupIdea.prediction_result))
            .order_by(StartupIdea.created_at.desc())
        )
        if params:
            stmt = stmt.offset(params.offset).limit(params.per_page)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_with_prediction(self, idea_id: str | UUID) -> Optional[StartupIdea]:
        if isinstance(idea_id, str):
            idea_id = UUID(idea_id)
        stmt = (
            select(StartupIdea)
            .where(StartupIdea.id == idea_id)
            .options(selectinload(StartupIdea.prediction_result))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_user(self, user_id: str | UUID, business_name: str) -> Optional[StartupIdea]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = select(StartupIdea).where(
            StartupIdea.user_id == user_id,
            func.lower(StartupIdea.business_name) == business_name.strip().lower(),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_by_user(self, user_id: str | UUID, limit: int = 5) -> List[StartupIdea]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        stmt = (
            select(StartupIdea)
            .where(StartupIdea.user_id == user_id)
            .options(selectinload(StartupIdea.prediction_result))
            .order_by(StartupIdea.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def filter_and_paginate(
        self,
        user_id: str | UUID,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_investment: Optional[float] = None,
        max_investment: Optional[float] = None,
        sort_by: str = "newest",
        params: Optional[PaginationParams] = None,
    ) -> PaginatedResult[StartupIdea]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        conditions = [StartupIdea.user_id == user_id]

        if query:
            q = f"%{query}%"
            conditions.append(
                or_(
                    StartupIdea.business_name.ilike(q),
                    StartupIdea.description.ilike(q),
                    StartupIdea.preferred_location.ilike(q),
                    StartupIdea.business_category.ilike(q),
                )
            )

        if category and category.lower() != "all":
            conditions.append(StartupIdea.business_category.ilike(f"%{category}%"))

        if min_investment is not None:
            conditions.append(StartupIdea.investment_amount >= min_investment)

        if max_investment is not None:
            conditions.append(StartupIdea.investment_amount <= max_investment)

        filter_expr = and_(*conditions)

        # Sorting logic
        sort_map = {
            "newest": desc(StartupIdea.created_at),
            "oldest": asc(StartupIdea.created_at),
            "highest_investment": desc(StartupIdea.investment_amount),
            "lowest_investment": asc(StartupIdea.investment_amount),
            "alphabetical": asc(StartupIdea.business_name),
        }
        order_clause = sort_map.get(sort_by, desc(StartupIdea.created_at))

        p = params or PaginationParams(page=1, per_page=20)
        
        # Query total count
        count_stmt = select(func.count()).select_from(StartupIdea).where(filter_expr)
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar_one() or 0

        # Query items
        stmt = (
            select(StartupIdea)
            .where(filter_expr)
            .options(selectinload(StartupIdea.prediction_result))
            .order_by(order_clause)
            .offset(p.offset)
            .limit(p.per_page)
        )
        items_res = await self.db.execute(stmt)
        items = list(items_res.scalars().all())

        return PaginatedResult.create(items=items, total=total, params=p)

    async def get_user_statistics(self, user_id: str | UUID) -> Dict[str, Any]:
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        # Total startups
        total_stmt = select(func.count()).select_from(StartupIdea).where(StartupIdea.user_id == user_id)
        total_res = await self.db.execute(total_stmt)
        total_count = total_res.scalar_one() or 0

        # Sum of investments
        inv_stmt = select(func.sum(StartupIdea.investment_amount)).where(StartupIdea.user_id == user_id)
        inv_res = await self.db.execute(inv_stmt)
        total_investment = inv_res.scalar_one() or 0.0

        # Latest startup
        latest_stmt = (
            select(StartupIdea)
            .where(StartupIdea.user_id == user_id)
            .order_by(StartupIdea.created_at.desc())
            .limit(1)
        )
        latest_res = await self.db.execute(latest_stmt)
        latest_startup = latest_res.scalar_one_or_none()

        # Category breakdown
        cat_stmt = (
            select(StartupIdea.business_category, func.count(StartupIdea.id))
            .where(StartupIdea.user_id == user_id)
            .group_by(StartupIdea.business_category)
        )
        cat_res = await self.db.execute(cat_stmt)
        category_counts = {cat: count for cat, count in cat_res.all()}

        return {
            "total_startups": total_count,
            "total_investment": float(total_investment),
            "avg_investment": float(total_investment / total_count) if total_count > 0 else 0.0,
            "latest_startup_name": latest_startup.business_name if latest_startup else None,
            "latest_startup_id": str(latest_startup.id) if latest_startup else None,
            "category_breakdown": category_counts,
        }
