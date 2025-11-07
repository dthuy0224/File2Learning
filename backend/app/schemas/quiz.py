from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


# Quiz Question schemas
class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str  # 'multiple_choice', 'fill_blank', 'true_false'
    correct_answer: str
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    difficulty_level: Optional[str] = 'medium'
    points: Optional[int] = 1


class QuizQuestionCreate(QuizQuestionBase):
    order_index: int


class QuizQuestion(QuizQuestionBase):
    id: int
    quiz_id: int
    order_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Quiz schemas
class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    quiz_type: str  # 'vocabulary', 'reading_comprehension', 'mixed'
    difficulty_level: Optional[str] = 'medium'
    time_limit: Optional[int] = None


class QuizCreate(QuizBase):
    document_id: Optional[int] = None
    questions: List[QuizQuestionCreate] = []


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: Optional[str] = None
    time_limit: Optional[int] = None


class Quiz(QuizBase):
    id: int
    document_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime
    questions: List[QuizQuestion] = []
    
    class Config:
        from_attributes = True


# Quiz Attempt schemas
class QuizAttemptCreate(BaseModel):
    quiz_id: int


class QuizAnswerSubmit(BaseModel):
    question_id: int
    answer: str
    time_taken: Optional[int] = None  # seconds for this question


class QuizAttemptSubmit(BaseModel):
    quiz_id: int
    answers: Dict[str, str]  # question_id -> answer
    total_time: Optional[int] = None  # total seconds


class QuizAttempt(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    answers: Dict[str, Dict[str, Any]]  # question_id -> detailed answer info
    score: int
    max_score: int
    percentage: int
    time_taken: Optional[int]
    is_completed: bool
    started_at: datetime
    completed_at: Optional[datetime]
    quiz: Optional['Quiz'] = None  

    class Config:
        from_attributes = True
