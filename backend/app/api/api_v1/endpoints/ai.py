from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import document
from app.schemas.document import Document
from app.schemas.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import ollama_service

router = APIRouter()


@router.post("/{document_id}/generate-quiz", response_model=Dict[str, Any])
async def generate_quiz_from_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    quiz_type: str = "mixed",
    num_questions: int = 5,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Generate quiz questions from a document using AI
    """
    # Get document
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if not document_obj.content:
        raise HTTPException(status_code=400, detail="Document has no content to process")

    try:
        # Generate quiz using Ollama (async operation)
        result = await ollama_service.generate_quiz(
            text_content=document_obj.content,
            quiz_type=quiz_type,
            num_questions=num_questions
        )

        if not result["success"]:
            # Return fallback quiz if AI failed
            return {
                "message": "AI generation failed, using fallback",
                "quiz": result.get("fallback", []),
                "error": result.get("error"),
                "document_id": document_id,
                "generated_by": "fallback"
            }

        # In a real implementation, you would save the quiz to database
        # For now, just return the generated quiz
        return {
            "message": "Quiz generated successfully",
            "quiz": result["quiz"],
            "document_id": document_id,
            "ai_model": result["ai_model"],
            "generated_by": "ollama"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {str(e)}"
        )


@router.post("/{document_id}/generate-flashcards", response_model=Dict[str, Any])
async def generate_flashcards_from_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    num_cards: int = 10,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate flashcards from a document using AI
    """
    # Get document
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if not document_obj.content:
        raise HTTPException(status_code=400, detail="Document has no content to process")

    try:
        # Generate flashcards using Ollama
        result = await ollama_service.generate_flashcards(
            text_content=document_obj.content,
            num_cards=num_cards
        )

        if not result["success"]:
            return {
                "message": "AI generation failed",
                "flashcards": [],
                "error": result.get("error"),
                "document_id": document_id
            }

        # In a real implementation, you would save flashcards to database
        return {
            "message": "Flashcards generated successfully",
            "flashcards": result["flashcards"],
            "document_id": document_id,
            "ai_model": result["ai_model"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating flashcards: {str(e)}"
        )


@router.post("/{document_id}/generate-summary", response_model=Dict[str, Any])
async def generate_summary_from_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    max_length: int = 300,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate summary from a document using AI
    """
    # Get document
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if not document_obj.content:
        raise HTTPException(status_code=400, detail="Document has no content to process")

    try:
        # Generate summary using Ollama
        result = await ollama_service.generate_summary(
            text_content=document_obj.content,
            max_length=max_length
        )

        if not result["success"]:
            return {
                "message": "AI generation failed",
                "summary": "",
                "error": result.get("error"),
                "document_id": document_id
            }

        # Update document summary in database
        from app.schemas.document import DocumentUpdate
        document_update = DocumentUpdate(summary=result["summary"])
        document_obj = document.update(db=db, db_obj=document_obj, obj_in=document_update)

        return {
            "message": "Summary generated successfully",
            "summary": result["summary"],
            "document_id": document_id,
            "ai_model": result["ai_model"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )


@router.get("/models", response_model=Dict[str, Any])
async def get_available_models() -> Any:
    """
    Get list of available Ollama models
    """
    try:
        # This would typically call Ollama API to list models
        # For now, return static list
        return {
            "models": [
                {
                    "name": "llama2:7b",
                    "description": "General purpose chat model",
                    "size": "3.8GB"
                },
                {
                    "name": "mistral:7b",
                    "description": "Fast and capable general model",
                    "size": "4.1GB"
                },
                {
                    "name": "codellama:7b",
                    "description": "Code-focused model",
                    "size": "3.8GB"
                }
            ],
            "default_model": "llama2:7b"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting models: {str(e)}"
        )


@router.post("/test-connection", response_model=Dict[str, Any])
async def test_ollama_connection() -> Any:
    """
    Test connection to Ollama service
    """
    try:
        # Simple test prompt
        test_result = await ollama_service.generate_summary(
            text_content="This is a test document for connection testing.",
            max_length=50
        )

        if test_result["success"]:
            return {
                "status": "connected",
                "message": "Ollama is working correctly",
                "model": test_result.get("ai_model", "unknown")
            }
        else:
            return {
                "status": "error",
                "message": "Ollama connection failed",
                "error": test_result.get("error", "Unknown error")
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }


@router.post("/{document_id}/chat", response_model=Dict[str, Any])
async def chat_with_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Chat with AI about a specific document
    """
    # Get document
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if not document_obj.content:
        raise HTTPException(status_code=400, detail="Document has no content to chat about")

    try:
        # Generate chat response using Ollama
        result = await ollama_service.generate_chat_response(
            text_content=document_obj.content,
            user_query=chat_request.query,
            chat_history=chat_request.conversation_history or []
        )

        if not result["success"]:
            return {
                "message": "AI chat failed",
                "answer": result.get("answer", "Unable to generate response"),
                "error": result.get("error"),
                "document_id": document_id,
                "success": False
            }

        return {
            "message": "Chat response generated successfully",
            "answer": result["answer"],
            "document_id": document_id,
            "ai_model": result["ai_model"],
            "success": True
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating chat response: {str(e)}"
        )
