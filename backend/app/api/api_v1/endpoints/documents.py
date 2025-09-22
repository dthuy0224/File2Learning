from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import document
from app.schemas.document import Document, DocumentCreate, DocumentUpdate
from app.schemas.user import User

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
    Upload a document file.
    """
    # This is a placeholder - file upload logic will be implemented later
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # TODO: Implement file processing
    # - Save file to disk
    # - Extract text content
    # - Create document record
    
    return {
        "message": f"File {file.filename} uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type
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


@router.delete("/{document_id}")
def delete_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a document.
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")
    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    document.remove(db=db, id=document_id)
    return {"message": "Document deleted successfully"}
