"""
STARTWISE AI — Marketing Service
High-level service for marketing strategies and recommendations.
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.marketing_repository import MarketingRepository
from app.schemas.schemas import MarketingStrategyOut


class MarketingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MarketingRepository(db)

    async def get_strategies_by_category(self, category: str) -> List[MarketingStrategyOut]:
        items = await self.repo.get_by_category(category)
        return [MarketingStrategyOut.model_validate(m) for m in items]
