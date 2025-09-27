"""Add OAuth fields to User model

Revision ID: 1234567890ab
Revises: 0801a1ea1a2c
Create Date: 2025-09-23 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = '653cee05936c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Add OAuth fields to users table ###
    op.add_column('users', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_email', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_avatar', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_oauth_account', sa.Boolean(), nullable=True))

    # Create indexes for OAuth fields
    op.create_index(op.f('ix_users_oauth_provider'), 'users', ['oauth_provider'], unique=False)
    op.create_index(op.f('ix_users_oauth_id'), 'users', ['oauth_id'], unique=False)
    op.create_index(op.f('ix_users_oauth_email'), 'users', ['oauth_email'], unique=False)
    op.create_index(op.f('ix_users_is_oauth_account'), 'users', ['is_oauth_account'], unique=False)

    # Set default value for is_oauth_account
    op.execute("UPDATE users SET is_oauth_account = false WHERE is_oauth_account IS NULL")


def downgrade() -> None:
    # ### Remove OAuth fields ###
    op.drop_index(op.f('ix_users_is_oauth_account'), table_name='users')
    op.drop_index(op.f('ix_users_oauth_email'), table_name='users')
    op.drop_index(op.f('ix_users_oauth_id'), table_name='users')
    op.drop_index(op.f('ix_users_oauth_provider'), table_name='users')
    op.drop_column('users', 'is_oauth_account')
    op.drop_column('users', 'oauth_avatar')
    op.drop_column('users', 'oauth_email')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
