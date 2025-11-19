from typing import Any, List, Dict
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
from app.models.quiz import QuizQuestion

router = APIRouter()


def _resolve_correct_answer_text(question: QuizQuestion, stored_answer: str) -> str:
    """
    Convert stored answer (which might be a letter) into human-readable text.
    For fill_blank questions, return the text directly (unless it's a letter and options exist - data error case).
    For multiple_choice questions, convert letter (A, B, C, D) to option text if needed.
    """
    answer_value = stored_answer or question.correct_answer or ""
    answer_value = answer_value.strip()
    
    # For fill_blank questions, correct_answer should be text, not a letter
    # But if it's a letter and options exist, it might be a data error - try to resolve
    if question.question_type == "fill_blank" or question.question_type == "fill_in_the_blank":
        # If it's a single letter and options exist, might be misclassified - try to resolve
        if len(answer_value) == 1 and answer_value.upper() in ["A", "B", "C", "D"] and question.options:
            index = ord(answer_value.upper()) - ord("A")
            if 0 <= index < len(question.options):
                return question.options[index]
        # Otherwise, return as-is (should be text for fill_blank)
        return answer_value or question.correct_answer
    
    # For multiple_choice or true_false, resolve letter to text if needed
    if not question.options:
        return answer_value or question.correct_answer

    if len(answer_value) == 1 and answer_value.upper() in ["A", "B", "C", "D"]:
        index = ord(answer_value.upper()) - ord("A")
        if 0 <= index < len(question.options):
            return question.options[index]
    return answer_value or question.correct_answer


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

        # Resolve correct_answer to human-readable text before storing
        resolved_correct_answer = _resolve_correct_answer_text(question, correct_answer)
        
        answers_dict[str(question_id)] = {
            "question_text": question.question_text,
            "user_answer": user_answer,
            "correct_answer": resolved_correct_answer,
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
    attempt_obj.score = sum(answer_data.get("points", 1) for answer_data in answers_dict.values() if answer_data.get("is_correct", False))
    attempt_obj.max_score = sum(question.points for question in questions)
    attempt_obj.percentage = int((attempt_obj.score / attempt_obj.max_score) * 100) if attempt_obj.max_score > 0 else 0
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

    attempt_obj = (
        db.query(QuizAttemptModel)
        .options(joinedload(QuizAttemptModel.quiz))
        .filter(QuizAttemptModel.id == attempt_id)
        .first()
    )

    if not attempt_obj:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")

    if attempt_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if attempt_obj.answers:
        question_ids = [int(qid) for qid in attempt_obj.answers.keys() if qid.isdigit()]
        if question_ids:
            question_objs = (
                db.query(QuizQuestion)
                .filter(QuizQuestion.id.in_(question_ids))
                .all()
            )
            question_map: Dict[str, QuizQuestion] = {str(q.id): q for q in question_objs}
            enriched_answers = {}

            for question_id, answer_data in attempt_obj.answers.items():
                question = question_map.get(question_id)
                if not question:
                    enriched_answers[question_id] = answer_data
                    continue

                enriched_entry = dict(answer_data or {})
                enriched_entry.setdefault("question_text", question.question_text)
                enriched_entry.setdefault("explanation", question.explanation)
                enriched_entry.setdefault("points", question.points)
                if question.options:
                    enriched_entry.setdefault("options", question.options)

                stored_correct = enriched_entry.get("correct_answer") or question.correct_answer
                enriched_entry["correct_answer"] = _resolve_correct_answer_text(
                    question, stored_correct
                )

                enriched_answers[question_id] = enriched_entry

            attempt_obj.answers = enriched_answers

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
