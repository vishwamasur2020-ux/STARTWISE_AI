"""add_otp_and_email_verification

Revision ID: c1a2b3d4e5f6
Revises: b8440b18ac6d
Create Date: 2026-10-07 23:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, None] = 'b8440b18ac6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add email_verified and email_verified_at to users table if not already present
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if "users" in existing_tables:
        existing_cols = [c["name"] for c in inspector.get_columns("users")]
        if "email_verified" not in existing_cols:
            op.add_column("users", sa.Column("email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False))
        if "email_verified_at" not in existing_cols:
            op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))

    # 2. Create otp_verifications table if not already present
    if "otp_verifications" not in existing_tables:
        op.create_table(
            "otp_verifications",
            sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("otp_hash", sa.String(length=255), nullable=False),
            sa.Column("purpose", sa.String(length=50), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("attempt_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
            sa.Column("max_attempts", sa.Integer(), server_default=sa.text("5"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_sent_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("ip_address", sa.String(length=45), nullable=True),
            sa.Column("user_agent", sa.String(length=500), nullable=True),
        )
        op.create_index("ix_otp_verifications_email", "otp_verifications", ["email"])
        op.create_index("ix_otp_verifications_purpose", "otp_verifications", ["purpose"])
        op.create_index("ix_otp_verifications_user_id", "otp_verifications", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if "otp_verifications" in existing_tables:
        op.drop_index("ix_otp_verifications_user_id", table_name="otp_verifications")
        op.drop_index("ix_otp_verifications_purpose", table_name="otp_verifications")
        op.drop_index("ix_otp_verifications_email", table_name="otp_verifications")
        op.drop_table("otp_verifications")

    if "users" in existing_tables:
        existing_cols = [c["name"] for c in inspector.get_columns("users")]
        if "email_verified_at" in existing_cols:
            op.drop_column("users", "email_verified_at")
        if "email_verified" in existing_cols:
            op.drop_column("users", "email_verified")
