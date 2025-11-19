import logging
import re
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from celery import chain

from celery import chain
from app.tasks.celery_app import celery_app
from app.utils.file_processor import FileProcessor
from app.core.database import SessionLocal
from app.crud import document as document_crud
from app.models.document import Document
from app.schemas.document import DocumentUpdate
from app.tasks.document_ai_tasks import (
    generate_document_summary_task,
    generate_document_vocabulary_task,
    generate_document_quiz_task,
)
from app.tasks.document_ai_tasks import (
    generate_document_summary_task,
    generate_document_vocabulary_task,
    generate_document_quiz_task,
)

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int, file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    Background task to process uploaded document
    """
    logger.info(f"Starting document processing for document_id: {document_id}")

    # Initialize metadata dictionary
    metadata = {}

    try:
        # Get file path object
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract text content
        file_extension = file_path_obj.suffix.lower()
        extracted_content = FileProcessor.extract_text_content(file_path_obj, file_extension)

        if not extracted_content or extracted_content.strip() == "":
            extracted_content = "No text content could be extracted from this file."
            logger.warning(f"No content extracted from document {document_id}")

        # Analyze content
        analysis = FileProcessor.analyze_content(extracted_content)

        # If content is invalid, mark as failed
        if not analysis.get("is_valid", False):
            error_message = f"Content validation failed: {', '.join(analysis.get('validation_errors', ['Unknown validation error']))}"
            _update_document_error_status(document_id, error_message)
            raise ValueError(error_message)

        # Clean up extracted content
        cleaned_content = clean_extracted_text(extracted_content)

        # Generate chunks for AI processing
        if len(cleaned_content) > FileProcessor.MAX_CHUNK_SIZE:
            optimal_chunk_size = FileProcessor.get_optimal_chunk_size(len(cleaned_content))
            chunks = FileProcessor.chunk_text(cleaned_content, max_chunk_size=optimal_chunk_size)
            metadata["chunks"] = chunks
            metadata["total_chunks"] = len(chunks)
            metadata["chunk_size"] = optimal_chunk_size
            logger.info(f"Document split into {len(chunks)} chunks for AI processing")
        else:
            metadata["chunks"] = None
            metadata["total_chunks"] = 1

        # Extract metadata if possible
        metadata.update(extract_document_metadata(file_path_obj, file_extension, cleaned_content))

        # Update database with processed data
        db = SessionLocal()
        try:
            document_obj = document_crud.get(db=db, id=document_id)
            if not document_obj:
                raise ValueError(f"Document {document_id} not found in database")

            # Update document with processed data
            update_data = DocumentUpdate(
                content=cleaned_content,
                word_count=analysis["word_count"],
                difficulty_level=analysis["difficulty_level"],
                processing_status='completed',
                processed_at=datetime.utcnow(),
                content_quality=analysis["content_quality"],
                quality_score=analysis["quality_score"],
                language_detected=analysis["language_detected"],
                encoding_issues=analysis["encoding_issues"],
                summary_status="queued",
                vocab_status="queued",
                quiz_status="queued",
                summary_error=None,
                vocab_error=None,
                quiz_error=None,
                **metadata
            )

            document_crud.update(db=db, db_obj=document_obj, obj_in=update_data)
            db.commit()

            logger.info(f"Successfully processed document {document_id}")

            # Trigger AI artifact generation in sequence (summary -> vocab -> quiz)
            chain(
                generate_document_summary_task.s(document_id=document_id),
                generate_document_vocabulary_task.s(document_id=document_id),
                generate_document_quiz_task.s(document_id=document_id),
            ).apply_async()

            return {
                "success": True,
                "document_id": document_id,
                "word_count": analysis["word_count"],
                "difficulty_level": analysis["difficulty_level"],
                "metadata": metadata,
                "processing_time": "completed",
                "ai_artifacts_queued": True,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Database error processing document {document_id}: {str(e)}")
            raise
        finally:
            db.close()

    except FileNotFoundError as e:
        logger.error(f"File not found for document {document_id}: {str(e)}")
        _update_document_error_status(document_id, f"File not found: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)

        # Update document status to failed with error details
        error_message = str(e)
        if len(error_message) > 500:  # Truncate long error messages
            error_message = error_message[:500] + "..."

        _update_document_error_status(document_id, error_message)

        # Retry logic with exponential backoff
        retry_count = self.request.retries
        if retry_count < self.max_retries:
            countdown = min(60 * (2 ** retry_count), 300)  # Max 5 minutes
            logger.info(f"Retrying document {document_id} in {countdown} seconds (attempt {retry_count + 1}/{self.max_retries + 1})")
            raise self.retry(countdown=countdown)
        else:
            logger.error(f"Max retries exceeded for document {document_id}")
            raise


def _update_document_error_status(document_id: int, error_message: str) -> None:
    """Update document status to failed with error message"""
    db = SessionLocal()
    try:
        document_obj = document_crud.get(db=db, id=document_id)
        if document_obj:
            error_update = DocumentUpdate(
                processing_status='failed',
                processing_error=error_message,
                processed_at=datetime.utcnow()
            )
            document_crud.update(db=db, db_obj=document_obj, obj_in=error_update)
            db.commit()
            logger.info(f"Updated document {document_id} status to failed")
    except Exception as db_error:
        logger.error(f"Error updating document {document_id} status: {str(db_error)}")
    finally:
        db.close()


def clean_extracted_text(text: str) -> str:
    """
    Comprehensive text cleaning and preprocessing
    """
    if not text:
        return ""

    import re

    # Step 1: Basic whitespace cleanup
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines to double
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n ', '\n', text)  # Remove space at end of lines

    # Step 2: Remove common PDF artifacts
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Lines with only numbers
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)  # Page numbers
    text = re.sub(r'-\n', '', text)  # Remove hyphenated line breaks

    # Step 3: Fix broken words at line endings
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)  # Join hyphenated words

    # Step 4: Remove excessive punctuation
    text = re.sub(r'[!?]+', '?', text)  # Multiple ? or ! to single
    text = re.sub(r'\.{3,}', '...', text)  # Multiple dots to ellipsis

    # Step 5: Fix spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([,.!?;:])\s+', r'\1 ', text)  # Ensure space after punctuation

    # Step 6: Remove common headers/footers
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip common header/footer patterns
        if (len(line) < 100 and
            re.match(r'^(chapter|section|part|page)\s+\d+', line.lower())):
            continue
        if re.match(r'^\d+$', line):  # Skip standalone numbers
            continue
        if len(line) < 3:  # Skip very short lines
            continue
        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Step 7: Final cleanup
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Clean up excessive newlines
    text = text.strip()

    # Log cleaning statistics
    original_length = len(text)
    cleaned_length = len(text)

    if original_length > 0:
        compression_ratio = (original_length - cleaned_length) / original_length
        logger.info(f"Text cleaning: {original_length} -> {cleaned_length} chars ({compression_ratio:.1%})")

    return text


def extract_document_metadata(file_path: Path, file_extension: str, content: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from document
    """
    metadata = {}

    try:
        # Extract title from content (first meaningful line)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if lines:
            # Look for first line that looks like a title (short, not starting with common words)
            potential_title = lines[0]
            if len(potential_title) < 100 and not potential_title.lower().startswith(('the', 'a', 'an', 'in', 'on', 'at', 'by', 'for', 'with', 'from')):
                metadata["extracted_title"] = potential_title

        # Extract author information (look for "by" patterns)
        author_patterns = [
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'author:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'written\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["extracted_author"] = match.group(1).strip()
                break

        # Extract creation date patterns
        date_patterns = [
            r'(?:created|written|published)\s+(?:on\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["extracted_date"] = match.group(1).strip()
                break

        # Extract topics/keywords (look for repeated important words)
        words = re.findall(r'\b[A-Za-z]{4,}\b', content.lower())
        word_counts = {}
        for word in words:
            if word not in ['that', 'with', 'from', 'this', 'they', 'have', 'been', 'will', 'would', 'could', 'should']:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Get top 10 most frequent meaningful words
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_words:
            metadata["extracted_keywords"] = [word for word, count in top_words if count > 1]

        # Extract reading time estimate (words per minute)
        word_count = len(content.split())
        estimated_reading_time = max(1, word_count // 200)  # Assume 200 WPM average
        metadata["estimated_reading_time_minutes"] = estimated_reading_time

        # Extract language indicators
        english_indicators = sum(1 for word in words if word in {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'
        })
        if english_indicators > len(words) * 0.1:
            metadata["detected_language"] = "english"

        # File metadata
        metadata["file_size_bytes"] = file_path.stat().st_size
        metadata["file_modified_time"] = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

        # Content structure analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sentences = []
        for paragraph in paragraphs:
            sentences.extend([s.strip() for s in paragraph.split('.') if s.strip()])

        metadata["paragraph_count"] = len(paragraphs)
        metadata["sentence_count"] = len(sentences)
        metadata["avg_sentence_length"] = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

    except Exception as e:
        logger.warning(f"Error extracting metadata: {str(e)}")

    return metadata
