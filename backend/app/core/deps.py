from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.crud.crud_user import user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    ✅ Get current authenticated user from:
    1️⃣ Authorization header (Bearer <token>)
    2️⃣ HttpOnly cookie (access_token)
    """

    token: Optional[str] = None

    # 1️⃣ Lấy token từ header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ")[1].strip()

    # 2️⃣ Nếu không có, lấy token từ cookie
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3️⃣ Xác minh token hợp lệ
    try:
        user_id = verify_token(token)
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4️⃣ Lấy user từ DB
    current_user = user.get(db, id=int(user_id))
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    print(f"✅ Authenticated user: {current_user.email} (ID={current_user.id})")
    return current_user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """✅ Returns only active users"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user
