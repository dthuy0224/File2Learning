"""rename learning_goals column to legacy_learning_goals

Revision ID: 2025111101
Revises: 2025111100
Create Date: 2025-11-11 15:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025111101'
down_revision = '2025111100'
branch_labels = None
depends_on = None


def upgrade():
    # Rename column to avoid conflict with relationship
    op.alter_column('users', 'learning_goals', new_column_name='legacy_learning_goals')


def downgrade():
    # Restore old name
    op.alter_column('users', 'legacy_learning_goals', new_column_name='learning_goals')

