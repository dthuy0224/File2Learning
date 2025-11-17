"""add key vocabulary column to documents

Revision ID: 2025111703
Revises: 2025111102_add_adaptive_recommendations_table
Create Date: 2025-11-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2025111703"
down_revision = "5e2d9bf5d30f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("key_vocabulary", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("documents", "key_vocabulary")

