"""add frontend contract fields

Revision ID: 0005_add_frontend_contract_fields
Revises: <PUT_PREVIOUS_REVISION_ID_HERE>
Create Date: 2026-01-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

revision = "0005_add_frontend_contract_fields"
down_revision ='0004_update_idempotency'

branch_labels = None
depends_on = None
def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table_name)]
    return column_name in cols
    
def upgrade():
    # Add description to categories
    if not _has_column("categories", "description"):
        op.add_column("categories", sa.Column("description", sa.Text(), nullable=True))

    # Add new fields to products
    op.add_column('products', sa.Column('old_price', sa.Numeric(12, 2), nullable=True))
    op.add_column('products', sa.Column('unit', sa.String(24), nullable=True))
    op.add_column('products', sa.Column('nutritional_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('products', sa.Column('is_organic', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # Add indexes
    op.create_index('ix_products_price', 'products', ['price'])
    op.create_index('ix_products_is_organic', 'products', ['is_organic'])

def downgrade():
    op.drop_index('ix_products_is_organic', table_name='products')
    op.drop_index('ix_products_price', table_name='products')
    op.drop_column('products', 'is_organic')
    op.drop_column('products', 'nutritional_info')
    op.drop_column('products', 'unit')
    op.drop_column('products', 'old_price')
    op.drop_column('categories', 'description')
