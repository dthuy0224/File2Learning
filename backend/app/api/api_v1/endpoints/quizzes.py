from typing import Any, List
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core import deps
from app.crud import quiz, flashcard
from app.tasks.learning_tasks import process_learning_event_task
from app.schemas.quiz import Quiz, QuizCreate, QuizUpdate, QuizAttempt, QuizAttemptCreate, QuizAttemptSubmit, QuizQuestionCreate
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=List[Quiz])
def read_quizzes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve quizzes for current user.
    """
    quizzes = quiz.get_by_user(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return quizzes


@router.get("/quick", response_model=Quiz)
def get_quick_quiz(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Generate a quick, random quiz from the user's flashcards.
    """
    user_flashcards = flashcard.get_by_user(db, user_id=current_user.id, limit=1000)

    if len(user_flashcards) < 4:
        raise HTTPException(status_code=400, detail="Not enough flashcards to generate a quiz. Please create at least 4 flashcards.")

    num_questions = min(10, len(user_flashcards))
    selected_cards = random.sample(user_flashcards, num_questions)

    questions = []
    for i, card in enumerate(selected_cards):
        other_cards = [c for c in user_flashcards if c.id != card.id]
        num_wrong_answers = min(3, len(other_cards))

        # Check edge case: if not enough cards to create wrong answers
        if num_wrong_answers > 0:
            wrong_cards = random.sample(other_cards, num_wrong_answers)
            wrong_answers = [c.back_text for c in wrong_cards]
        else:
            wrong_answers = ["Option A", "Option B", "Option C"]

        options = wrong_answers + [card.back_text]
        random.shuffle(options)

        question = QuizQuestionCreate(
            question_text=f"What is the definition of '{card.front_text}'?",
            question_type="multiple_choice",
            options=options,
            correct_answer=card.back_text,
            points=1,
            order_index=i + 1
        )
        questions.append(question)

    
    return {
        "id": 0, 
        "title": "Quick Vocabulary Quiz",
        "description": "A quick quiz generated from your flashcards.",
        "quiz_type": "vocabulary",
        "difficulty_level": "medium",
        "created_by": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "questions": questions
    }


@router.post("/", response_model=Quiz)
def create_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_in: QuizCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new quiz.
    """
    quiz_obj = quiz.create_with_creator(
        db=db, obj_in=quiz_in, creator_id=current_user.id
    )
    return quiz_obj


@router.get("/{quiz_id}", response_model=Quiz)
def read_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get quiz by ID.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz_obj


@router.put("/{quiz_id}", response_model=Quiz)
def update_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    quiz_in: QuizUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a quiz.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz_obj.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    quiz_obj = quiz.update(db=db, db_obj=quiz_obj, obj_in=quiz_in)
    return quiz_obj


@router.post("/{quiz_id}/attempt", response_model=QuizAttempt)
def start_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Start a new quiz attempt.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")

    
    from app.models.quiz import QuizAttempt
    from datetime import datetime

    attempt_obj = QuizAttempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        answers={}, 
        score=0,     
        max_score=0, 
        percentage=0, 
        time_taken=None, 
        is_completed=False,
        started_at=datetime.utcnow(),
        completed_at=None
    )

    db.add(attempt_obj)
    db.commit()
    db.refresh(attempt_obj)

    return attempt_obj


@router.post("/{quiz_id}/submit", response_model=QuizAttempt)
def submit_quiz_attempt(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    submission: QuizAttemptSubmit,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Submit quiz attempt answers.
    """
    quiz_obj = quiz.get(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")

    
    from app.models.quiz import QuizQuestion
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()

    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    
    correct_answers = 0
    total_points = 0
    answers_dict = {}

    for question in questions:
        question_id = question.id
        user_answer = submission.answers.get(str(question_id), "")
        correct_answer = question.correct_answer
        
        # Smart answer comparison
        is_correct = False
        
        # Case 1: Direct match (for fill-in-the-blank or exact match)
        if user_answer.strip().lower() == correct_answer.strip().lower():
            is_correct = True
        # Case 2: Multiple choice - check if user selected the correct option
        elif question.options and len(correct_answer) == 1 and correct_answer.upper() in ['A', 'B', 'C', 'D']:
            # Correct answer is a letter (A, B, C, D)
            option_index = ord(correct_answer.upper()) - ord('A')
            if 0 <= option_index < len(question.options):
                correct_option_text = question.options[option_index]
                if user_answer.strip().lower() == correct_option_text.strip().lower():
                    is_correct = True
        # Case 3: User answered with letter, correct answer is text
        elif user_answer.strip().upper() in ['A', 'B', 'C', 'D'] and question.options:
            option_index = ord(user_answer.strip().upper()) - ord('A')
            if 0 <= option_index < len(question.options):
                user_option_text = question.options[option_index]
                if user_option_text.strip().lower() == correct_answer.strip().lower():
                    is_correct = True

        answers_dict[str(question_id)] = {
            "question_text": question.question_text,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation,
            "points": question.points
        }
        
        if is_correct:
            correct_answers += 1

        total_points += question.points

    
    percentage = int((correct_answers / len(questions)) * 100) if questions else 0

    
    from app.models.quiz import QuizAttempt 
    from datetime import datetime            

    attempt_obj = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.is_completed == False
    ).first()

    if not attempt_obj:
        raise HTTPException(status_code=400, detail="No active quiz attempt found")

            
    attempt_obj.answers = answers_dict
    attempt_obj.score = correct_answers * (100 // len(questions)) if questions else 0  # Score out of 100
    attempt_obj.max_score = 100
    attempt_obj.percentage = percentage
    attempt_obj.time_taken = submission.total_time
    attempt_obj.is_completed = True
    attempt_obj.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt_obj)

    # Trigger adaptive learning updates asynchronously
    try:
        process_learning_event_task.delay(
            user_id=current_user.id,
            event_type="quiz_completed",
            payload={
                "quiz_id": quiz_id,
                "attempt_id": attempt_obj.id,
                "percentage": percentage,
                "score": attempt_obj.score,
                "correct_answers": correct_answers,
                "total_questions": len(questions),
            },
        )
    except Exception as background_error:  # pragma: no cover - log path
        import logging

        logging.getLogger(__name__).warning(
            "Failed to enqueue learning event for quiz %s (user %s): %s",
            quiz_id,
            current_user.id,
            background_error,
        )

    return attempt_obj


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttempt])
def read_quiz_attempts(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's attempts for a specific quiz.
    """
    attempts = quiz.get_user_attempts(
        db=db, user_id=current_user.id, quiz_id=quiz_id
    )
    return attempts


@router.get("/attempts/{attempt_id}", response_model=QuizAttempt)
def read_quiz_attempt_by_id(
    *,
    db: Session = Depends(get_db),
    attempt_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:

    from app.models.quiz import QuizAttempt as QuizAttemptModel
    from sqlalchemy.orm import joinedload

    attempt_obj = db.query(QuizAttemptModel)\
        .options(joinedload(QuizAttemptModel.quiz))\
        .filter(QuizAttemptModel.id == attempt_id)\
        .first()

    if not attempt_obj:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")

    if attempt_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return attempt_obj


@router.delete("/{quiz_id}")
def delete_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a quiz.
    """
    quiz_obj = quiz.remove(db=db, id=quiz_id)
    if not quiz_obj:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if quiz_obj.created_by != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return {"message": "Quiz deleted successfully"}
