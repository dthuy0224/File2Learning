from typing import Any
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status,
    Body,
)
from sqlalchemy.orm import Session
import shutil
import os
import re

from app.core.database import get_db
from app.core import deps
from app.core.security import pwd_context
from app.crud import user as crud_user
from app.models.user import User as UserModel
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserOut,
    PasswordChange,
)

router = APIRouter()

AVATAR_DIR = "app/static/avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)



@router.post("/", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    if crud_user.get_by_email(db, email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud_user.get_by_username(db, username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud_user.create(db, obj_in=user_in)



@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    data: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_user),
):
    updated_user = crud_user.update(db, db_obj=current_user, obj_in=data)
    return updated_user



@router.get("/me", response_model=UserOut)
def read_user_me(current_user: UserModel = Depends(deps.get_current_user)):
    """Return current user info + whether they need onboarding setup."""
    user_data = UserOut.model_validate(current_user)
    user_data.needs_setup = not (
        current_user.learning_goals
        and len(current_user.learning_goals) > 0
        and current_user.difficulty_preference
        and current_user.daily_study_time
    )
    return user_data



from app.schemas.user import LearningSetup

@router.put("/me/setup-learning", response_model=UserOut)
def setup_learning_preferences(
    *,
    db: Session = Depends(get_db),
    setup: LearningSetup,
    current_user: UserModel = Depends(deps.get_current_user),
):
    current_user.learning_goals = setup.learning_goals
    current_user.difficulty_preference = setup.difficulty_preference
    current_user.daily_study_time = setup.daily_study_time

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user



@router.post("/me/change-password")
def change_password(
    *,
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    user = crud_user.change_password(
        db,
        user_id=current_user.id,
        old_password=data.old_password,
        new_password=data.new_password,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid old password")
    return {"message": "Password updated successfully"}



@router.post("/me/upload-avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    filename = f"user_{current_user.id}_{safe_filename}"
    file_path = os.path.join(AVATAR_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    current_user.avatar = filename
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    avatar_url = f"http://localhost:8000/static/avatars/{filename}"
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "avatar_url": avatar_url,
        "learning_goals": current_user.learning_goals,
        "difficulty_preference": current_user.difficulty_preference,
        "daily_study_time": current_user.daily_study_time,
        "created_at": current_user.created_at,
    }



@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    *,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(deps.get_current_user),
):
    user_obj = crud_user.get(db, id=user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    if user_obj.id != current_user.id and not crud_user.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return user_obj
