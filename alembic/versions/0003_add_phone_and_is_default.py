"""Add phone to users and is_default to addresses"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0003_add_phone_and_is_default"
down_revision = "0002_add_idempotency_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Add phone column to users table if it doesn't exist
    users_columns = [col["name"] for col in inspector.get_columns("users")]
    if "phone" not in users_columns:
        op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    
    # Add is_default column to addresses table if it doesn't exist
    addresses_columns = [col["name"] for col in inspector.get_columns("addresses")]
    if "is_default" not in addresses_columns:
        op.add_column(
            "addresses",
            sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        )


def downgrade() -> None:
    op.drop_column("addresses", "is_default")
    op.drop_column("users", "phone")
