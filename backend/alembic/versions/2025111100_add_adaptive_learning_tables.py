from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025111100'
down_revision = ('161ff7b04b04', '87de4ed7d545', 'af74cf50d9ae')  # Merge all heads
branch_labels = None
depends_on = None


def upgrade():
    # Create learning_profiles table
    op.create_table(
        'learning_profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('learning_style', sa.String(), nullable=True, server_default='balanced'),
        sa.Column('preferred_difficulty', sa.String(), nullable=True, server_default='medium'),
        sa.Column('optimal_study_times', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('avg_session_duration', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('avg_daily_study_time', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_streak', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_activity_date', sa.DateTime(), nullable=True),
        sa.Column('overall_retention_rate', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('quiz_accuracy_rate', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('flashcard_success_rate', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('weak_topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('strong_topics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_velocity', sa.DECIMAL(5, 2), nullable=True, server_default='1.00'),
        sa.Column('recommended_daily_load', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('last_performance_analysis', sa.DateTime(), nullable=True),
        sa.Column('last_schedule_adjustment', sa.DateTime(), nullable=True),
        sa.Column('adaptation_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('preferred_study_days', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('break_preference', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
        sa.CheckConstraint('overall_retention_rate >= 0 AND overall_retention_rate <= 100', name='chk_retention_rate'),
        sa.CheckConstraint('quiz_accuracy_rate >= 0 AND quiz_accuracy_rate <= 100', name='chk_quiz_accuracy'),
        sa.CheckConstraint('flashcard_success_rate >= 0 AND flashcard_success_rate <= 100', name='chk_flashcard_success'),
        sa.CheckConstraint('learning_velocity > 0', name='chk_learning_velocity'),
        sa.CheckConstraint('current_streak >= 0', name='chk_current_streak'),
        sa.CheckConstraint('longest_streak >= 0', name='chk_longest_streak'),
        sa.CheckConstraint('avg_session_duration > 0', name='chk_session_duration'),
        sa.CheckConstraint('recommended_daily_load > 0', name='chk_daily_load'),
    )
    op.create_index(op.f('ix_learning_profiles_user_id'), 'learning_profiles', ['user_id'], unique=False)

    # Create learning_goals table
    op.create_table(
        'learning_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal_type', sa.String(), nullable=False),
        sa.Column('goal_title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('current_progress', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('actual_completion_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='active'),
        sa.Column('priority', sa.String(), nullable=True, server_default='medium'),
        sa.Column('is_on_track', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('days_behind', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('estimated_completion_date', sa.Date(), nullable=True),
        sa.Column('completion_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('milestones', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("target_date >= start_date", name='chk_goal_dates'),
        sa.CheckConstraint("status IN ('draft', 'active', 'paused', 'completed', 'abandoned')", name='chk_goal_status'),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name='chk_goal_priority'),
        sa.CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", name='chk_completion_percentage'),
        sa.CheckConstraint("days_behind >= 0", name='chk_days_behind'),
    )
    op.create_index(op.f('ix_learning_goals_id'), 'learning_goals', ['id'], unique=False)
    op.create_index(op.f('ix_learning_goals_user_id'), 'learning_goals', ['user_id'], unique=False)

    # Create study_schedules table
    op.create_table(
        'study_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), nullable=True),
        sa.Column('schedule_name', sa.String(), nullable=False),
        sa.Column('schedule_type', sa.String(), nullable=False),
        sa.Column('schedule_config', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('milestones', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('adaptation_mode', sa.String(), nullable=True, server_default='moderate'),
        sa.Column('max_daily_load', sa.Integer(), nullable=True, server_default='60'),
        sa.Column('min_daily_load', sa.Integer(), nullable=True, server_default='15'),
        sa.Column('catch_up_strategy', sa.String(), nullable=True, server_default='gradual'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('effectiveness_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('total_days_scheduled', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('days_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('days_missed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('days_partially_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_adherence_rate', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('last_adjusted_at', sa.DateTime(), nullable=True),
        sa.Column('adjustment_reason', sa.Text(), nullable=True),
        sa.Column('adjustment_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('deactivated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['goal_id'], ['learning_goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("max_daily_load >= min_daily_load", name='chk_load_range'),
        sa.CheckConstraint("adaptation_mode IN ('strict', 'moderate', 'flexible', 'highly_adaptive')", name='chk_adaptation_mode'),
        sa.CheckConstraint("catch_up_strategy IN ('skip', 'gradual', 'intensive')", name='chk_catch_up_strategy'),
        sa.CheckConstraint("total_days_scheduled >= 0", name='chk_total_days'),
        sa.CheckConstraint("days_completed >= 0", name='chk_days_completed'),
        sa.CheckConstraint("days_missed >= 0", name='chk_days_missed'),
        sa.CheckConstraint("avg_adherence_rate >= 0 AND avg_adherence_rate <= 100", name='chk_adherence_rate'),
    )
    op.create_index(op.f('ix_study_schedules_id'), 'study_schedules', ['id'], unique=False)
    op.create_index(op.f('ix_study_schedules_user_id'), 'study_schedules', ['user_id'], unique=False)
    op.create_index(op.f('ix_study_schedules_is_active'), 'study_schedules', ['is_active'], unique=False)

    # Create daily_study_plans table
    op.create_table(
        'daily_study_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=True),
        sa.Column('plan_date', sa.Date(), nullable=False),
        sa.Column('plan_summary', sa.Text(), nullable=True),
        sa.Column('recommended_tasks', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('total_estimated_minutes', sa.Integer(), nullable=False),
        sa.Column('actual_minutes_spent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('priority_level', sa.String(), nullable=True, server_default='normal'),
        sa.Column('difficulty_level', sa.String(), nullable=True, server_default='medium'),
        sa.Column('is_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('completion_percentage', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('completed_tasks_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_tasks_count', sa.Integer(), nullable=False),
        sa.Column('actual_performance', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='pending'),
        sa.Column('skip_reason', sa.String(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('effectiveness_rating', sa.Integer(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['schedule_id'], ['study_schedules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'partially_completed', 'skipped')", name='chk_plan_status'),
        sa.CheckConstraint("priority_level IN ('low', 'normal', 'high', 'critical')", name='chk_priority_level'),
        sa.CheckConstraint("difficulty_level IN ('easy', 'medium', 'hard')", name='chk_difficulty_level'),
        sa.CheckConstraint("completion_percentage >= 0 AND completion_percentage <= 100", name='chk_completion_pct'),
        sa.CheckConstraint("total_tasks_count > 0", name='chk_tasks_count'),
        sa.CheckConstraint("completed_tasks_count >= 0", name='chk_completed_count'),
        sa.CheckConstraint("effectiveness_rating IS NULL OR (effectiveness_rating >= 1 AND effectiveness_rating <= 5)", name='chk_effectiveness'),
    )
    op.create_index(op.f('ix_daily_study_plans_id'), 'daily_study_plans', ['id'], unique=False)
    op.create_index(op.f('ix_daily_study_plans_user_id'), 'daily_study_plans', ['user_id'], unique=False)
    op.create_index(op.f('ix_daily_study_plans_plan_date'), 'daily_study_plans', ['plan_date'], unique=False)
    op.create_index(op.f('ix_daily_study_plans_is_completed'), 'daily_study_plans', ['is_completed'], unique=False)

    # Create study_sessions table
    op.create_table(
        'study_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('daily_plan_id', sa.Integer(), nullable=True),
        sa.Column('session_type', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=False),
        sa.Column('performance_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('accuracy_rate', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('items_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('items_correct', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('device_type', sa.String(), nullable=True),
        sa.Column('time_of_day', sa.String(), nullable=True),
        sa.Column('is_planned', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('focus_score', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('interruptions_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('primary_topic', sa.String(), nullable=True),
        sa.Column('difficulty_attempted', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['daily_plan_id'], ['daily_study_plans.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("duration_seconds > 0", name='chk_duration'),
        sa.CheckConstraint("ended_at > started_at", name='chk_session_times'),
        sa.CheckConstraint("accuracy_rate IS NULL OR (accuracy_rate >= 0 AND accuracy_rate <= 100)", name='chk_accuracy'),
        sa.CheckConstraint("focus_score IS NULL OR (focus_score >= 0 AND focus_score <= 100)", name='chk_focus'),
        sa.CheckConstraint("items_completed >= 0", name='chk_items_completed'),
        sa.CheckConstraint("items_correct >= 0", name='chk_items_correct'),
        sa.CheckConstraint("interruptions_count >= 0", name='chk_interruptions'),
    )
    op.create_index(op.f('ix_study_sessions_id'), 'study_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_study_sessions_user_id'), 'study_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_study_sessions_session_type'), 'study_sessions', ['session_type'], unique=False)
    op.create_index(op.f('ix_study_sessions_started_at'), 'study_sessions', ['started_at'], unique=False)

    # Create learning_analytics table
    op.create_table(
        'learning_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analytics_date', sa.Date(), nullable=False),
        sa.Column('total_study_minutes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('sessions_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('flashcards_reviewed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('flashcards_correct', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('flashcard_accuracy', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('quizzes_taken', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('quiz_avg_score', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('quiz_total_questions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('quiz_correct_answers', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('documents_read', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('words_learned', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('overall_accuracy', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('focus_score', sa.DECIMAL(5, 2), nullable=True, server_default='0.00'),
        sa.Column('topic_performance', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('identified_weak_areas', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('identified_strong_areas', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('vs_yesterday_improvement', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('vs_week_ago_improvement', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('vs_personal_best', sa.DECIMAL(5, 2), nullable=True),
        sa.Column('is_active_day', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('streak_maintained', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('daily_goal_met', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('most_productive_time', sa.String(), nullable=True),
        sa.Column('study_time_distribution', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("total_study_minutes >= 0", name='chk_study_minutes'),
        sa.CheckConstraint("sessions_count >= 0", name='chk_sessions_count'),
        sa.CheckConstraint("flashcards_reviewed >= 0", name='chk_flashcards_reviewed'),
        sa.CheckConstraint("quizzes_taken >= 0", name='chk_quizzes_taken'),
        sa.CheckConstraint("documents_read >= 0", name='chk_documents_read'),
        sa.CheckConstraint("overall_accuracy >= 0 AND overall_accuracy <= 100", name='chk_overall_accuracy'),
    )
    op.create_index(op.f('ix_learning_analytics_id'), 'learning_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_learning_analytics_user_id'), 'learning_analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_learning_analytics_analytics_date'), 'learning_analytics', ['analytics_date'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_learning_analytics_analytics_date'), table_name='learning_analytics')
    op.drop_index(op.f('ix_learning_analytics_user_id'), table_name='learning_analytics')
    op.drop_index(op.f('ix_learning_analytics_id'), table_name='learning_analytics')
    op.drop_table('learning_analytics')

    op.drop_index(op.f('ix_study_sessions_started_at'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_session_type'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_user_id'), table_name='study_sessions')
    op.drop_index(op.f('ix_study_sessions_id'), table_name='study_sessions')
    op.drop_table('study_sessions')

    op.drop_index(op.f('ix_daily_study_plans_is_completed'), table_name='daily_study_plans')
    op.drop_index(op.f('ix_daily_study_plans_plan_date'), table_name='daily_study_plans')
    op.drop_index(op.f('ix_daily_study_plans_user_id'), table_name='daily_study_plans')
    op.drop_index(op.f('ix_daily_study_plans_id'), table_name='daily_study_plans')
    op.drop_table('daily_study_plans')

    op.drop_index(op.f('ix_study_schedules_is_active'), table_name='study_schedules')
    op.drop_index(op.f('ix_study_schedules_user_id'), table_name='study_schedules')
    op.drop_index(op.f('ix_study_schedules_id'), table_name='study_schedules')
    op.drop_table('study_schedules')

    op.drop_index(op.f('ix_learning_goals_user_id'), table_name='learning_goals')
    op.drop_index(op.f('ix_learning_goals_id'), table_name='learning_goals')
    op.drop_table('learning_goals')

    op.drop_index(op.f('ix_learning_profiles_user_id'), table_name='learning_profiles')
    op.drop_table('learning_profiles')

