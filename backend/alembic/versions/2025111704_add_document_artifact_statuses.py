"""add artifact generation statuses to documents

Revision ID: 2025111704
Revises: 2025111703
Create Date: 2025-11-17 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2025111704"
down_revision = "2025111703"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("summary_status", sa.String(), nullable=False, server_default="pending"),
    )
    op.add_column("documents", sa.Column("summary_error", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("summary_generated_at", sa.DateTime(), nullable=True))

    op.add_column(
        "documents",
        sa.Column("vocab_status", sa.String(), nullable=False, server_default="pending"),
    )
    op.add_column("documents", sa.Column("vocab_error", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("vocab_generated_at", sa.DateTime(), nullable=True))

    op.add_column(
        "documents",
        sa.Column("quiz_status", sa.String(), nullable=False, server_default="pending"),
    )
    op.add_column("documents", sa.Column("quiz_error", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("quiz_generated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("documents", "quiz_generated_at")
    op.drop_column("documents", "quiz_error")
    op.drop_column("documents", "quiz_status")
    op.drop_column("documents", "vocab_generated_at")
    op.drop_column("documents", "vocab_error")
    op.drop_column("documents", "vocab_status")
    op.drop_column("documents", "summary_generated_at")
    op.drop_column("documents", "summary_error")
    op.drop_column("documents", "summary_status")

