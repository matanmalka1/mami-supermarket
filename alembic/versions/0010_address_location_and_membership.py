"""
Add GPS columns to addresses and membership tier to users.
"""
from alembic import op
import sqlalchemy as sa

# Alembic identifiers
revision = "0010_address_location_and_membership"
down_revision = "0009_add_image_url_to_products"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("addresses", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("addresses", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "membership_tier",
            sa.String(length=32),
            nullable=False,
            server_default="FREE",
        ),
    )


def downgrade():
    op.drop_column("users", "membership_tier")
    op.drop_column("addresses", "longitude")
    op.drop_column("addresses", "latitude")
