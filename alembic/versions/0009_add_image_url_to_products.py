"""
Add image_url column to products table
"""
from alembic import op
import sqlalchemy as sa

# Alembic revision identifiers
revision = '0009_add_image_url_to_products'
down_revision = '0008_add_bin_location_to_products'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('products', sa.Column('image_url', sa.String(length=255), nullable=True))
    op.create_index('ix_products_image_url', 'products', ['image_url'])

def downgrade():
    op.drop_index('ix_products_image_url', table_name='products')
    op.drop_column('products', 'image_url')
