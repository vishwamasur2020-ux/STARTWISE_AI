"""
STARTWISE AI — Database Mixins & Pagination Helpers
Reusable SQLAlchemy 2.0 mixins for primary keys, timestamps, and pagination logic.
"""

import uuid
from datetime import datetime, timezone
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column

T = TypeVar("T")


# ─── Primary Key Mixin ───────────────────────────────────────────────────────
class UUIDMixin:
    """Provides a UUID v4 primary key `id` column."""
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


# ─── Timestamp Mixin ─────────────────────────────────────────────────────────
class TimestampMixin:
    """Provides timezone-aware `created_at` and `updated_at` timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ─── Pagination Request & Response Helpers ────────────────────────────────────
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class PaginatedResult(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "PaginatedResult[T]":
        pages = (total + params.per_page - 1) // params.per_page if total > 0 else 1
        return cls(
            items=items,
            total=total,
            page=params.page,
            per_page=params.per_page,
            pages=pages,
        )
