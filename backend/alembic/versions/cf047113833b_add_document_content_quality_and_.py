"""Add document content quality and language detection fields

Revision ID: cf047113833b
Revises: 9b6ae480157e
Create Date: 2025-09-29 21:23:51.278193

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf047113833b'
down_revision = '9b6ae480157e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add content_quality column
    op.add_column('documents', sa.Column('content_quality', sa.String(), nullable=True))

    # Add quality_score column
    op.add_column('documents', sa.Column('quality_score', sa.Integer(), nullable=True))

    # Add language_detected column
    op.add_column('documents', sa.Column('language_detected', sa.String(), nullable=True))

    # Add encoding_issues column
    op.add_column('documents', sa.Column('encoding_issues', sa.Integer(), nullable=True, default=0))


def downgrade() -> None:
    # Remove encoding_issues column
    op.drop_column('documents', 'encoding_issues')

    # Remove language_detected column
    op.drop_column('documents', 'language_detected')

    # Remove quality_score column
    op.drop_column('documents', 'quality_score')

    # Remove content_quality column
    op.drop_column('documents', 'content_quality')
