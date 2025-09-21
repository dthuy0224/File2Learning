"""Add performance indexes

Revision ID: 653cee05936c
Revises: 0801a1ea1a2c
Create Date: 2025-09-21 14:59:39.222097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '653cee05936c'
down_revision = '0801a1ea1a2c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Performance indexes for common queries ###
    
    # Index for flashcard spaced repetition queries
    op.create_index(
        'idx_flashcards_next_review', 
        'flashcards', 
        ['owner_id', 'next_review_date']
    )
    
    # Index for document queries by owner and creation date
    op.create_index(
        'idx_documents_owner_created', 
        'documents', 
        ['owner_id', 'created_at']
    )
    
    # Index for quiz attempt analytics
    op.create_index(
        'idx_quiz_attempts_user_completed', 
        'quiz_attempts', 
        ['user_id', 'completed_at']
    )
    
    # Index for flashcard performance tracking
    op.create_index(
        'idx_flashcards_owner_document', 
        'flashcards', 
        ['owner_id', 'document_id']
    )
    
    # Index for quiz questions ordering
    op.create_index(
        'idx_quiz_questions_quiz_order', 
        'quiz_questions', 
        ['quiz_id', 'order_index']
    )
    
    # Index for document processing status
    op.create_index(
        'idx_documents_processed_at', 
        'documents', 
        ['processed_at']
    )


def downgrade() -> None:
    # ### Drop performance indexes ###
    
    op.drop_index('idx_documents_processed_at', table_name='documents')
    op.drop_index('idx_quiz_questions_quiz_order', table_name='quiz_questions')
    op.drop_index('idx_flashcards_owner_document', table_name='flashcards')
    op.drop_index('idx_quiz_attempts_user_completed', table_name='quiz_attempts')
    op.drop_index('idx_documents_owner_created', table_name='documents')
    op.drop_index('idx_flashcards_next_review', table_name='flashcards')
