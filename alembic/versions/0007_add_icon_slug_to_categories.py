"""
Add icon_slug to categories table and index.
"""
from alembic import op
import sqlalchemy as sa

revision = '0007_add_icon_slug_to_categories'
down_revision = '0006_expand_alembic_version_num_length'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('categories', sa.Column('icon_slug', sa.String(length=64), nullable=True))
    op.create_index('ix_categories_icon_slug', 'categories', ['icon_slug'], unique=False)

def downgrade():
    op.drop_index('ix_categories_icon_slug', table_name='categories')
    op.drop_column('categories', 'icon_slug')
