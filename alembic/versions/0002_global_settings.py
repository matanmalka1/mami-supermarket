"""Add global_settings table."""

revision = "0002_global_settings"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade() -> None:
    op.create_table(
        "global_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("delivery_min", sa.Numeric(precision=10, scale=2), nullable=False, server_default="50.0"),
        sa.Column("delivery_fee", sa.Numeric(precision=10, scale=2), nullable=False, server_default="15.0"),
        sa.Column("free_threshold", sa.Numeric(precision=10, scale=2), nullable=False, server_default="200.0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Insert default settings row
    op.execute("""
        INSERT INTO global_settings (delivery_min, delivery_fee, free_threshold)
        VALUES (150.0, 30.0, 200.0)
    """)


def downgrade() -> None:
    op.drop_table("global_settings")
