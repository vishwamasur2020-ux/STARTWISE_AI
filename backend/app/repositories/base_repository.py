"""
STARTWISE AI — Generic Base Repository
Abstract async repository implementing CRUD operations, pagination, search filtering, and counts.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy import select, func, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import Base
from app.database.mixins import PaginationParams, PaginatedResult
from app.core.logging import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async Repository pattern implementation for SQLAlchemy 2.0 ORM models."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: str | UUID) -> Optional[ModelType]:
        if isinstance(id, str):
            id = UUID(id)
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        logger.info(f"Created {self.model.__name__} record: {getattr(instance, 'id', None)}")
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for field, value in kwargs.items():
            if hasattr(instance, field) and value is not None:
                setattr(instance, field, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.db.delete(instance)
        await self.db.flush()

    async def delete_by_id(self, id: str | UUID) -> bool:
        instance = await self.get_by_id(id)
        if instance:
            await self.delete(instance)
            return True
        return False

    async def get_all(self, skip: int = 0, limit: int = 20) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self, filter_condition: Optional[Any] = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        if filter_condition is not None:
            stmt = stmt.where(filter_condition)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def paginate(
        self,
        params: PaginationParams,
        filter_condition: Optional[Any] = None,
        order_by: Optional[Any] = None,
    ) -> PaginatedResult[ModelType]:
        stmt = select(self.model)
        if filter_condition is not None:
            stmt = stmt.where(filter_condition)
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        # Count total
        total = await self.count(filter_condition)

        # Apply offset and limit
        stmt = stmt.offset(params.offset).limit(params.per_page)
        result = await self.db.execute(stmt)
        items = list(result.scalars().all())

        return PaginatedResult.create(items=items, total=total, params=params)
