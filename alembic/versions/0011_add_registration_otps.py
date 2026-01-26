"""
Create the registration OTP table for temporary codes.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic identifiers
revision = "0011_add_registration_otps"
down_revision = "0010_address_location_and_membership"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "registration_otps",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=False), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_registration_otps_email", "registration_otps", ["email"])


def downgrade():
    op.drop_index("ix_registration_otps_email", table_name="registration_otps")
    op.drop_table("registration_otps")
