"""add adaptive_recommendations table

Revision ID: 2025111102
Revises: 2025111101
Create Date: 2025-11-11 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025111102'
down_revision = '2025111101'
branch_labels = None
depends_on = None


def upgrade():
    # Create adaptive_recommendations table
    op.create_table(
        'adaptive_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum(
            'review_flashcard', 'study_topic', 'take_quiz', 'read_document',
            'focus_weak_area', 'reinforce_strength',
            name='recommendationtype'
        ), nullable=False),
        sa.Column('priority', sa.Enum(
            'low', 'medium', 'high', 'urgent',
            name='recommendationpriority'
        ), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('target_resource_type', sa.String(length=50), nullable=True),
        sa.Column('target_resource_id', sa.Integer(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('expected_impact', sa.Float(), nullable=True),
        sa.Column('is_viewed', sa.Integer(), nullable=True),
        sa.Column('is_accepted', sa.Integer(), nullable=True),
        sa.Column('is_dismissed', sa.Integer(), nullable=True),
        sa.Column('viewed_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_adaptive_recommendations_id', 'adaptive_recommendations', ['id'])
    op.create_index('ix_adaptive_recommendations_user_id', 'adaptive_recommendations', ['user_id'])
    op.create_index('ix_adaptive_recommendations_type', 'adaptive_recommendations', ['type'])
    op.create_index('ix_adaptive_recommendations_priority', 'adaptive_recommendations', ['priority'])
    op.create_index('ix_adaptive_recommendations_created_at', 'adaptive_recommendations', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_adaptive_recommendations_created_at', table_name='adaptive_recommendations')
    op.drop_index('ix_adaptive_recommendations_priority', table_name='adaptive_recommendations')
    op.drop_index('ix_adaptive_recommendations_type', table_name='adaptive_recommendations')
    op.drop_index('ix_adaptive_recommendations_user_id', table_name='adaptive_recommendations')
    op.drop_index('ix_adaptive_recommendations_id', table_name='adaptive_recommendations')
    
    # Drop table
    op.drop_table('adaptive_recommendations')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS recommendationtype')
    op.execute('DROP TYPE IF EXISTS recommendationpriority')

