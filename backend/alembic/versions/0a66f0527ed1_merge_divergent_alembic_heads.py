"""Merge divergent alembic heads

Revision ID: 0a66f0527ed1
Revises: 1aff3c5774ce, e7ee7c3685cc
Create Date: 2025-11-20 02:55:31.725298

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a66f0527ed1'
down_revision = ('1aff3c5774ce', 'e7ee7c3685cc')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
