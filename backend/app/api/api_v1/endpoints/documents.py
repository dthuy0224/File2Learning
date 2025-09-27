from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import document
from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.schemas.user import User
from app.utils.file_processor import process_uploaded_file

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
    Upload a document file and process it.
    Supports PDF, DOCX, DOC, and TXT files.
    """
    # Read file content
    content = await file.read()
    file_size = len(content)

    # Process file using service
    try:
        result = process_uploaded_file(file.filename, file_size, content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

    # Create document record
    document_in = DocumentCreate(
        filename=result["filename"],
        original_filename=file.filename,
        file_path=str(result["file_path"]),
        file_size=file_size,
        document_type=result["file_extension"][1:],  # Remove the dot
        content=result["extracted_content"],
        word_count=result["word_count"],
        difficulty_level=result["difficulty_level"],
        title=file.filename.split('.')[0]  # Use filename without extension as title
    )

    try:
        document_obj = document.create_with_owner(
            db=db, obj_in=document_in, owner_id=current_user.id
        )
    except Exception as e:
        # Clean up file if database operation fails
        result["file_path"].unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document record: {str(e)}"
        )

    return {
        "message": "Document uploaded and processed successfully",
        "document_id": document_obj.id,
        "filename": file.filename,
        "file_size": file_size,
        "word_count": result["word_count"],
        "document_type": result["file_extension"][1:],
        "difficulty_level": result["difficulty_level"],
        "status": "processed"
    }


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
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Delete physical file if exists
    if document_obj.file_path:
        file_path = Path(document_obj.file_path)
        if file_path.exists():
            file_path.unlink()

    # Delete document record
    document.remove(db=db, id=document_id)
    return {"message": "Document deleted successfully"}


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

    return {
        "document_id": document_obj.id,
        "status": "processed" if document_obj.processed_at else "processing",
        "filename": document_obj.original_filename,
        "document_type": document_obj.document_type,
        "word_count": document_obj.word_count,
        "difficulty_level": document_obj.difficulty_level,
        "file_size": document_obj.file_size,
        "created_at": document_obj.created_at,
        "processed_at": document_obj.processed_at,
        "title": document_obj.title
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
