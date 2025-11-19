from typing import Any, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import document, quiz as quiz_crud, flashcard as flashcard_crud
from app.schemas.document import Document, DocumentUpdate
from app.schemas.user import User
from app.schemas.chat import ChatRequest
from app.schemas.quiz import QuizCreate, QuizQuestionCreate, Quiz as QuizSchema
from app.schemas.flashcard import FlashcardCreate, Flashcard as FlashcardSchema
from app.services.multi_ai_service import multi_ai_service

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
        # Generate quiz using Multi-AI Service (Gemini/Groq/Ollama)
        result = await multi_ai_service.generate_quiz(
            text_content=document_obj.content,
            quiz_type=quiz_type,
            num_questions=num_questions
        )

        if not result["success"]:
            return {
                "message": "AI generation failed, using fallback",
                "quiz": result.get("fallback", []),
                "error": result.get("error"),
                "document_id": document_id,
                "generated_by": "fallback"
            }

        quiz_questions = []
        for idx, question in enumerate(result["quiz"], start=1):
            question_text = question.get("question") or question.get("question_text")
            if not question_text:
                continue

            question_options = question.get("options")
            question_type_value = question.get("question_type")
            if not question_type_value:
                question_type_value = "multiple_choice" if question_options else "fill_blank"

            quiz_questions.append(
                QuizQuestionCreate(
                    question_text=question_text.strip(),
                    question_type=question_type_value,
                    correct_answer=question.get("correct_answer", "").strip(),
                    options=question_options or [],
                    explanation=question.get("explanation") or "",
                    difficulty_level=question.get("difficulty_level", document_obj.difficulty_level or "medium"),
                    points=question.get("points", 1),
                    order_index=idx,
                )
            )

        if not quiz_questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI did not return any valid quiz questions"
            )

        quiz_title = f"{document_obj.title or document_obj.original_filename} - AI Quiz"
        timestamp_suffix = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

        quiz_in = QuizCreate(
            title=f"{quiz_title} ({timestamp_suffix})",
            description=f"AI-generated {quiz_type} quiz for {document_obj.title or document_obj.original_filename}",
            quiz_type=quiz_type,
            difficulty_level=document_obj.difficulty_level or "medium",
            time_limit=None,
            document_id=document_obj.id,
            questions=quiz_questions
        )

        quiz_obj = quiz_crud.create_with_creator(
            db=db,
            obj_in=quiz_in,
            creator_id=current_user.id
        )

        quiz_schema = QuizSchema.from_orm(quiz_obj)
        quiz_questions_payload = []
        for question in quiz_schema.questions:
            question_dict = question.dict()
            question_dict.setdefault("question", question_dict.get("question_text", ""))
            quiz_questions_payload.append(question_dict)

        return {
            "message": "Quiz generated and saved successfully",
            "document_id": document_id,
            "quiz_id": quiz_obj.id,
            "question_count": len(quiz_questions),
            "ai_provider": result["ai_provider"],
            "ai_model": result["ai_model"],
            "generated_by": result["ai_provider"],
            "quiz": quiz_questions_payload,
            "quiz_details": quiz_schema.dict()
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
        # Generate flashcards using Multi-AI Service
        result = await multi_ai_service.generate_flashcards(
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

        created_flashcards = []
        for card in result["flashcards"]:
            if not card.get("front_text") or not card.get("back_text"):
                continue

            flashcard_in = FlashcardCreate(
                front_text=card["front_text"].strip("* "),
                back_text=card["back_text"].strip(),
                example_sentence=card.get("example_sentence"),
                pronunciation=None,
                word_type=None,
                difficulty_level=document_obj.difficulty_level or "medium",
                tags=None,
                document_id=document_obj.id
            )
            flashcard_obj = flashcard_crud.create_with_owner(
                db=db,
                obj_in=flashcard_in,
                owner_id=current_user.id
            )
            created_flashcards.append(FlashcardSchema.from_orm(flashcard_obj).dict())

        return {
            "message": "Flashcards generated and saved successfully",
            "flashcards": created_flashcards,
            "flashcards_created": created_flashcards,
            "document_id": document_id,
            "ai_provider": result.get("ai_provider", "unknown"),
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
        # Generate summary using Multi-AI Service
        result = await multi_ai_service.generate_summary(
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

        key_vocab_result = await multi_ai_service.generate_key_vocabulary(
            text_content=document_obj.content,
            num_terms=8
        )

        key_vocab = key_vocab_result["key_vocabulary"] if key_vocab_result["success"] else document_obj.key_vocabulary

        document_update = DocumentUpdate(
            summary=result["summary"],
            key_vocabulary=key_vocab
        )
        document_obj = document.update(db=db, db_obj=document_obj, obj_in=document_update)

        return {
            "message": "Summary generated successfully",
            "summary": result["summary"],
            "key_vocabulary": key_vocab,
            "document_id": document_id,
            "ai_provider": result.get("ai_provider", "unknown"),
            "ai_model": result["ai_model"],
            "original_length": result["original_length"],
            "summary_length": result["summary_length"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )


@router.post("/{document_id}/generate-key-vocabulary", response_model=Dict[str, Any])
async def generate_key_vocabulary_from_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    num_terms: int = 8,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate key vocabulary list for a document using AI
    """
    document_obj = document.get(db=db, id=document_id)
    if not document_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    if document_obj.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if not document_obj.content:
        raise HTTPException(status_code=400, detail="Document has no content to process")

    try:
        result = await multi_ai_service.generate_key_vocabulary(
            text_content=document_obj.content,
            num_terms=num_terms
        )

        if not result["success"]:
            return {
                "message": "AI generation failed",
                "key_vocabulary": [],
                "error": result.get("error"),
                "document_id": document_id
            }

        document_update = DocumentUpdate(key_vocabulary=result["key_vocabulary"])
        document_obj = document.update(db=db, db_obj=document_obj, obj_in=document_update)

        return {
            "message": "Key vocabulary generated successfully",
            "document_id": document_id,
            "key_vocabulary": document_obj.key_vocabulary,
            "ai_provider": result.get("ai_provider", "unknown"),
            "ai_model": result["ai_model"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating key vocabulary: {str(e)}"
        )


@router.get("/models", response_model=Dict[str, Any])
async def get_available_models() -> Any:
    """
    Get list of available AI models
    """
    return {
        "models": [
            {
                "name": "gemini-2.0-flash-exp",
                "provider": "Google Gemini",
                "description": "Latest Gemini model (FREE)",
                "status": "available"
            },
            {
                "name": "llama-3.3-70b-versatile",
                "provider": "Groq",
                "description": "Fast and capable model (FREE)",
                "status": "available"
            }
        ],
        "default_provider": "gemini",
        "default_model": "gemini-2.0-flash-exp"
    }


@router.post("/test-connection", response_model=Dict[str, Any])
async def test_ai_connection() -> Any:
    """
    Test connection to Multi-AI Service (Gemini/Groq)
    """
    try:
        # Simple test prompt
        test_result = await multi_ai_service.generate_summary(
            text_content="This is a test document for connection testing.",
            max_length=50
        )

        if test_result["success"]:
            return {
                "status": "connected",
                "message": "AI service is working correctly! 🎉",
                "provider": test_result.get("ai_provider", "unknown"),
                "model": test_result.get("ai_model", "unknown"),
                "stats": multi_ai_service.get_stats()
            }
        else:
            return {
                "status": "error",
                "message": "All AI providers failed",
                "error": test_result.get("error", "Unknown error"),
                "stats": multi_ai_service.get_stats()
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }


@router.get("/stats", response_model=Dict[str, Any])
async def get_ai_stats() -> Any:
    """
    Get AI service usage statistics
    """
    try:
        stats = multi_ai_service.get_stats()
        return {
            "success": True,
            "stats": stats,
            "message": "AI service statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )


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
        # Generate chat response using Multi-AI Service
        result = await multi_ai_service.generate_chat_response(
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
            "ai_provider": result.get("ai_provider", "unknown"),
            "ai_model": result["ai_model"],
            "success": True
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating chat response: {str(e)}"
        )
