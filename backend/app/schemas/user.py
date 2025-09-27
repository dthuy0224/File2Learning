from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    learning_goals: Optional[List[str]] = []
    difficulty_preference: Optional[str] = 'medium'
    daily_study_time: Optional[int] = 30

    # OAuth fields
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    oauth_email: Optional[str] = None
    oauth_avatar: Optional[str] = None
    is_oauth_account: bool = False

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

    # OAuth fields (optional for regular registration)
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    oauth_email: Optional[str] = None
    oauth_avatar: Optional[str] = None
    is_oauth_account: bool = False


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    oauth_email: Optional[str] = None
    oauth_avatar: Optional[str] = None
    is_oauth_account: Optional[bool] = None


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return to client
class User(UserInDBBase):
    pass


# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
