"""Add document processing status fields

Revision ID: 161ff7b04b04
Revises: dcb8e558a9d6
Create Date: 2025-09-29 13:08:14.125396

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '161ff7b04b04'
down_revision = '0801a1ea1a2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add processing_status column
    op.add_column('documents', sa.Column('processing_status', sa.String(), nullable=True, default='pending'))

    # Add processing_error column
    op.add_column('documents', sa.Column('processing_error', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove processing_error column
    op.drop_column('documents', 'processing_error')

    # Remove processing_status column
    op.drop_column('documents', 'processing_status')
