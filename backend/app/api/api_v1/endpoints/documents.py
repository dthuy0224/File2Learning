from typing import Any, List, Dict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import document
from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentCreateFromTopic
from app.schemas.user import User
from app.utils.file_processor import FileProcessor, SecurityScanner
from app.tasks.document_tasks import process_document_task
from app.services.ai_service import ollama_service

router = APIRouter()


@router.get("/", response_model=List[Document])
def read_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    documents = document.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return documents

@router.post("/", response_model=Document)
def create_document(
    *,
    db: Session = Depends(get_db),
    document_in: DocumentCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    document_obj = document.create_with_owner(
        db=db, obj_in=document_in, owner_id=current_user.id
    )
    return document_obj


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Upload a document file for background processing.
    Supports PDF, DOCX, DOC, and TXT files.
    """
    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file
    file_extension = FileProcessor.validate_file(file.filename, file_size)

    # Generate unique filename and path
    sanitized_filename, file_path = FileProcessor.generate_unique_filename(file.filename)

    # Save file to disk
    FileProcessor.save_file(file_path, content)

    # Security scan
    security_scan = SecurityScanner.scan_file_content(content.decode('utf-8', errors='ignore'), file.filename)

    if not security_scan["is_safe"]:
        # Clean up file if security scan fails
        FileProcessor.cleanup_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File failed security scan: {', '.join(security_scan['issues'][:3])}"
        )

    # Create document record with pending status
    document_in = DocumentCreate(
        filename=sanitized_filename,
        original_filename=file.filename,
        file_path=str(file_path.resolve()),
        file_size=file_size,
        document_type=file_extension[1:],  # Remove the dot
        title=file.filename.split('.')[0],  # Use filename without extension as title
        processing_status='pending'
    )

    try:
        document_obj = document.create_with_owner(
            db=db, obj_in=document_in, owner_id=current_user.id
        )

        # Trigger background processing
        process_document_task.delay(
            document_id=document_obj.id,
            file_path=str(file_path.resolve()),
            original_filename=file.filename
        )

        return {
            "message": "Document uploaded successfully. Processing in background.",
            "document_id": document_obj.id,
            "filename": file.filename,
            "file_size": file_size,
            "document_type": file_extension[1:],
            "status": "pending",
            "processing_message": "Document is being processed. Check status endpoint for updates."
        }

    except Exception as e:
        # Clean up file if database operation fails
        FileProcessor.cleanup_file(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document record: {str(e)}"
        )


@router.get("/{document_id}", response_model=Document)
def read_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get document by ID.
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document_obj


@router.put("/{document_id}", response_model=Document)
def update_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a document.
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    document_obj = document.update(db=db, db_obj=document_obj, obj_in=document_in)
    return document_obj


@router.get("/{document_id}/content")
def get_document_content(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get document content (extracted text).
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    return {
        "document_id": document_obj.id,
        "title": document_obj.title,
        "content": document_obj.content,
        "word_count": document_obj.word_count,
        "document_type": document_obj.document_type,
        "created_at": document_obj.created_at
    }


@router.delete("/{document_id}")
def delete_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a document and its associated file.
    """
    document_obj = document.remove(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Delete physical file if exists
    if document_obj.file_path:
        try:
            # Build absolute path assuming project root is /app in container
            project_root = Path("/app")
            full_file_path = project_root / document_obj.file_path

            if full_file_path.exists():
                full_file_path.unlink()
                print(f"Successfully deleted file: {full_file_path}")
            else:
                print(f"File not found for deletion: {full_file_path}")

        except Exception as e:
            # Log error but don't crash the entire request
            # Database record deletion is more important
            print(f"Error deleting physical file: {str(e)}")

    return {"message": "Document deleted successfully"}


@router.post("/from-topic", response_model=Document, status_code=201)
async def create_document_from_topic(
    *,
    db: Session = Depends(get_db),
    topic_in: DocumentCreateFromTopic,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new document from a topic provided by the user, using AI.
    """
    # Step 1: Call AI Service to generate content
    generation_result = await ollama_service.generate_document_from_topic(topic_in.topic)
    if not generation_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"AI failed to generate content: {generation_result['error']}"
        )

    generated_content = generation_result["content"]

    # Step 2: Create Document object in DB
    doc_in = DocumentCreate(
        filename=f"AI Generated - {topic_in.topic}.txt",
        original_filename=f"AI Generated - {topic_in.topic}.txt", # Add this line
        file_path=f"uploads/ai_generated/{topic_in.topic}.txt", # Add fake file path
        file_size=len(generated_content), # Add file size
        document_type="txt", # Add file type
        content=generated_content
    )
    document_obj = document.create_with_owner(db=db, obj_in=doc_in, owner_id=current_user.id)

    # Step 3: Update document status to completed since we already have the content
    # No need for background processing since content is already generated
    from datetime import datetime
    update_data = DocumentUpdate(
        processing_status='completed',
        processed_at=datetime.utcnow(),
        word_count=len(generated_content.split())
    )
    document.update(db=db, db_obj=document_obj, obj_in=update_data)

    return document_obj


@router.get("/{document_id}/status")
def get_document_status(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get document processing status and details.
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Calculate processing progress
    progress_info = _calculate_processing_progress(document_obj)

    return {
        "document_id": document_obj.id,
        "status": document_obj.processing_status,
        "filename": document_obj.original_filename,
        "document_type": document_obj.document_type,
        "word_count": document_obj.word_count,
        "difficulty_level": document_obj.difficulty_level,
        "file_size": document_obj.file_size,
        "content_quality": document_obj.content_quality,
        "quality_score": document_obj.quality_score,
        "language_detected": document_obj.language_detected,
        "encoding_issues": document_obj.encoding_issues,
        "created_at": document_obj.created_at,
        "processed_at": document_obj.processed_at,
        "processing_error": document_obj.processing_error,
        "title": document_obj.title,
        "progress": progress_info
    }


@router.get("/status/batch", response_model=Dict[str, Any])
def get_documents_status_batch(
    *,
    db: Session = Depends(get_db),
    document_ids: str,  # Comma-separated document IDs
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get processing status for multiple documents.
    Usage: /status/batch?document_ids=1,2,3
    """
    try:
        ids = [int(id_str.strip()) for id_str in document_ids.split(',') if id_str.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document IDs format")

    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents per batch request")

    results = {}
    for doc_id in ids:
        try:
            document_obj = document.get(db=db, id=doc_id)
            if not document_obj:
                results[str(doc_id)] = {"error": "Document not found"}
                continue

            if document_obj.owner_id != current_user.id:
                results[str(doc_id)] = {"error": "Not enough permissions"}
                continue

            progress_info = _calculate_processing_progress(document_obj)
            results[str(doc_id)] = {
                "status": document_obj.processing_status,
                "filename": document_obj.original_filename,
                "document_type": document_obj.document_type,
                "word_count": document_obj.word_count,
                "difficulty_level": document_obj.difficulty_level,
                "content_quality": document_obj.content_quality,
                "quality_score": document_obj.quality_score,
                "language_detected": document_obj.language_detected,
                "encoding_issues": document_obj.encoding_issues,
                "created_at": document_obj.created_at,
                "processed_at": document_obj.processed_at,
                "processing_error": document_obj.processing_error,
                "progress": progress_info
            }
        except Exception as e:
            results[str(doc_id)] = {"error": str(e)}

    return {
        "documents": results,
        "total_requested": len(ids),
        "total_returned": len(results)
    }


def _calculate_processing_progress(document_obj) -> Dict[str, Any]:
    """
    Calculate processing progress and estimated completion
    """
    status = document_obj.processing_status
    created_at = document_obj.created_at

    if not created_at:
        return {"percentage": 0, "stage": "unknown", "estimated_completion": None}

    current_time = datetime.utcnow()
    elapsed_time = (current_time - created_at).total_seconds()

    if status == "completed":
        return {
            "percentage": 100,
            "stage": "completed",
            "estimated_completion": document_obj.processed_at,
            "actual_completion": document_obj.processed_at
        }
    elif status == "failed":
        return {
            "percentage": 0,
            "stage": "failed",
            "estimated_completion": None,
            "error": document_obj.processing_error
        }
    elif status == "processing":
        # Estimate progress based on elapsed time (rough heuristic)
        # Processing typically takes 2-10 seconds per MB
        file_size_mb = document_obj.file_size / (1024 * 1024) if document_obj.file_size else 1
        estimated_total_time = max(file_size_mb * 3, 10)  # At least 10 seconds
        progress_percentage = min((elapsed_time / estimated_total_time) * 100, 95)  # Max 95% until actually completed

        estimated_completion = created_at + timedelta(seconds=estimated_total_time)

        return {
            "percentage": round(progress_percentage, 1),
            "stage": "processing",
            "estimated_completion": estimated_completion.isoformat(),
            "elapsed_time_seconds": round(elapsed_time, 1)
        }
    else:  # pending
        return {
            "percentage": 0,
            "stage": "pending",
            "estimated_completion": None,
            "queue_position": "waiting_for_processing"
        }


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Reprocess an existing document.
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Check if file still exists
    if not Path(document_obj.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original file not found. Cannot reprocess."
        )

    # Re-extract content
    file_extension = f".{document_obj.document_type}"
    extracted_content = ""

    try:
        if file_extension == ".pdf":
            import pdfplumber
            with pdfplumber.open(document_obj.file_path) as pdf:
                for page in pdf.pages:
                    extracted_content += page.extract_text() + "\n"
        elif file_extension in {".docx", ".doc"}:
            from docx import Document
            doc = Document(document_obj.file_path)
            extracted_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file_extension == ".txt":
            with open(document_obj.file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_content = f.read()

        # Clean up extracted content
        extracted_content = extracted_content.strip()
        if not extracted_content:
            extracted_content = "No text content could be extracted from this file."

    except Exception as e:
        extracted_content = f"Error extracting content: {str(e)}"

    # Calculate word count
    word_count = len(extracted_content.split()) if extracted_content else 0

    # Determine difficulty level
    difficulty_level = "easy" if word_count < 500 else "medium" if word_count < 2000 else "hard"

    # Update document
    document_update = DocumentUpdate(
        content=extracted_content,
        word_count=word_count,
        difficulty_level=difficulty_level
    )

    try:
        document_obj = document.update(db=db, db_obj=document_obj, obj_in=document_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating document: {str(e)}"
        )

    return {
        "message": "Document reprocessed successfully",
        "document_id": document_obj.id,
        "word_count": word_count,
        "difficulty_level": difficulty_level,
        "status": "processed"
    }
