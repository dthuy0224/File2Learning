from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime




class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    learning_goals: Optional[List[str]] = None
    difficulty_preference: Optional[str] = None
    daily_study_time: Optional[int] = None
    avatar_url: Optional[str] = None

    # OAuth fields
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    oauth_email: Optional[str] = None
    oauth_avatar: Optional[str] = None
    is_oauth_account: bool = False



class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: Optional[str] = None


class UserUpdate(UserBase):
    full_name: Optional[str]
    learning_goals: Optional[List[str]]
    difficulty_preference: Optional[str]
    daily_study_time: Optional[int]
    avatar_url: Optional[str] = None

class LearningSetup(BaseModel):
    learning_goals: List[str]
    difficulty_preference: str
    daily_study_time: int

class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserInDBBase):
    hashed_password: str


class User(UserInDBBase):
    """Schema đại diện cho user khi trả về từ DB."""
    pass



class UserResponse(UserInDBBase):
    id: int
    is_active: bool


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    learning_goals: Optional[List[str]]
    difficulty_preference: Optional[str]
    daily_study_time: Optional[int]
    created_at: datetime
    oauth_avatar: Optional[str]
    avatar_url: Optional[str] = None
    needs_setup: Optional[bool] = None   # <--- Add this line

    class Config:
        from_attributes = True





class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None



class PasswordChange(BaseModel):
    old_password: constr(min_length=6)
    new_password: constr(min_length=6)

class AvatarUploadResponse(BaseModel):
    avatar_url: str


class ProgressOverTime(BaseModel):
    month: str
    progress: int

class RetentionDataItem(BaseModel):
    name: str
    value: int

class QuizByTopic(BaseModel):
    topic: str
    score: float

class LearningAnalytics(BaseModel):
    words_learned: int
    retention_rate: float
    avg_quiz_score: float
    progress: float
    active_days: int
    progress_over_time: List[ProgressOverTime]
    retention_data: List[RetentionDataItem]
    quiz_by_topic: List[QuizByTopic]
