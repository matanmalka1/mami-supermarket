"""
Add bin_location column to products table
"""
from alembic import op
import sqlalchemy as sa

# Alembic revision identifiers
revision = '0008_add_bin_location_to_products'
down_revision = '0007_add_icon_slug_to_categories'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('products', sa.Column('bin_location', sa.String(length=32), nullable=True))
    op.create_index('ix_products_bin_location', 'products', ['bin_location'])

def downgrade():
    op.drop_index('ix_products_bin_location', table_name='products')
    op.drop_column('products', 'bin_location')
