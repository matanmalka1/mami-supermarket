"""
Expand alembic_version.version_num to VARCHAR(255) for long revision IDs.
"""
from alembic import op
import sqlalchemy as sa

# Alembic revision identifiers
revision = '0006_expand_alembic_version_num_length'
down_revision = '0005_add_frontend_contract_fields'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255) USING version_num::VARCHAR(255);")

def downgrade():
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(32) USING version_num::VARCHAR(32);")
