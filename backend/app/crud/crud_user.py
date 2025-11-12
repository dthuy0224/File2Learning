from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    # ===== GET methods =====
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_id(self, db: Session, *, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    # ===== CREATE =====
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        hashed_password = None
        if not obj_in.is_oauth_account:
            if not obj_in.password:
                raise ValueError("Password is required for non-OAuth users")
            hashed_password = get_password_hash(obj_in.password)

        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            legacy_learning_goals=obj_in.learning_goals,
            difficulty_preference=obj_in.difficulty_preference,
            daily_study_time=obj_in.daily_study_time,
            oauth_provider=obj_in.oauth_provider,
            oauth_id=obj_in.oauth_id,
            oauth_email=obj_in.oauth_email,
            oauth_avatar=obj_in.oauth_avatar,
            is_oauth_account=obj_in.is_oauth_account,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # ===== UPDATE =====
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        db_obj.updated_at = datetime.utcnow()
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # ===== AUTH =====
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        OAuth accounts cannot login with password - they must use OAuth flow.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None

        # OAuth accounts cannot login with password
        if user.is_oauth_account:
            return None

        # Check if user has a password set
        if not user.hashed_password:
            return None

        # Verify password
        if not verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        return user

    # ===== PASSWORD CHANGE =====
    def change_password(self, db: Session, *, user_id: int, old_password: str, new_password: str) -> Optional[User]:
        user = self.get_by_id(db, user_id=user_id)
        if not user or not verify_password(old_password, user.hashed_password):
            return None
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    # ===== AVATAR UPLOAD =====
    def upload_avatar(self, db: Session, *, user_id: int, avatar_url: str) -> Optional[User]:
        user = self.get_by_id(db, user_id=user_id)
        if not user:
            return None
        user.oauth_avatar = avatar_url
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    
    def is_active(self, user: User) -> bool:
            return user.is_active

user = CRUDUser(User)
