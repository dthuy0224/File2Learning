# backend/app/api/api_v1/endpoints/auth.py
"""
Auth endpoints:
- Local: register, login, logout, forgot-password, reset-password
- OAuth: /oauth/{provider}  -> trả authorization_url + state
         /oauth/{provider}/callback -> exchange code, create user (auto-register), issue JWT, set cookie, redirect to frontend
Uses Redis for:
 - storing oauth state (CSRF protection)
 - optional token blacklist for logout
If Redis not configured, falls back to in-memory store (NOT for production).
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import secrets
import logging
from urllib.parse import quote
from urllib.parse import urlencode
import httpx
from fastapi import Response
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.email import send_email
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.crud import user as crud_user
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema, UserResponse
from app.core import deps
from app.services.oauth_service import get_oauth_service

# Optional Redis client — create file app/core/redis.py that exports `redis_client`
try:
    from app.core.redis import redis_client  # type: ignore
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory fallback stores (only for dev / single-process)
IN_MEMORY_OAUTH_STATE: Dict[str, str] = {}
IN_MEMORY_BLACKLIST: Dict[str, float] = {}


def save_oauth_state(state: str, provider: str, ttl_seconds: int = 300) -> None:
    key = f"oauth_state:{state}"
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.setex(key, ttl_seconds, provider)
            return
        except Exception as e:
            logger.warning("Redis setex failed, falling back to memory store: %s", e)
    IN_MEMORY_OAUTH_STATE[state] = provider


def get_oauth_state(state: str) -> Optional[str]:
    key = f"oauth_state:{state}"
    if REDIS_AVAILABLE and redis_client:
        try:
            return redis_client.get(key)
        except Exception as e:
            logger.warning("Redis get failed, falling back to memory store: %s", e)
    return IN_MEMORY_OAUTH_STATE.get(state)


def pop_oauth_state(state: str) -> None:
    key = f"oauth_state:{state}"
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.delete(key)
            return
        except Exception:
            pass
    IN_MEMORY_OAUTH_STATE.pop(state, None)


def blacklist_token(token: str, expires_in_seconds: int) -> None:
    if not token:
        return
    key = f"blacklist:{token}"
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.setex(key, expires_in_seconds, "1")
            return
        except Exception as e:
            logger.warning("Redis setex failed when blacklisting token: %s", e)
    IN_MEMORY_BLACKLIST[token] = datetime.utcnow().timestamp() + expires_in_seconds


def is_token_blacklisted(token: str) -> bool:
    if not token:
        return False
    key = f"blacklist:{token}"
    if REDIS_AVAILABLE and redis_client:
        try:
            val = redis_client.get(key)
            return val is not None
        except Exception:
            logger.warning("Redis get failed in is_token_blacklisted, falling back to memory")
    expiry = IN_MEMORY_BLACKLIST.get(token)
    if expiry and expiry > datetime.utcnow().timestamp():
        return True
    if expiry:
        IN_MEMORY_BLACKLIST.pop(token, None)
    return False


# ===========================
# Local register / login
# ===========================
@router.post("/register", response_model=UserResponse)
def register_user(new_user: UserCreate, db: Session = Depends(get_db)):
    # Check email trùng
    if crud_user.get_by_email(db, email=new_user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check username trùng
    if crud_user.get_by_username(db, username=new_user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        created = crud_user.create(db, obj_in=new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username already exists")

    return created


@router.post("/login", response_model=Token)
def login_access_token(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login with email/password (OAuth2 password flow form).
    Sets HttpOnly cookie 'access_token' AND returns token JSON for compatibility.
    """
    logger.info(f"Login attempt for email: {form_data.username}")
    user_obj = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user_obj:
        logger.warning(f"Authentication failed for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password. If you signed up with OAuth, please use OAuth login instead."
        )
    if not crud_user.is_active(user_obj):
        logger.warning(f"Inactive user attempted login: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    logger.info(f"Successful login for user: {user_obj.email} (ID={user_obj.id})")

    access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt = security.create_access_token(subject=str(user_obj.id), expires_delta=access_expires)

    # Clear any previous cookie and set new one
    response.delete_cookie("access_token", path="/")
    response.set_cookie(
        key="access_token",
        value=jwt,
        httponly=True,
        secure=settings.FRONTEND_URL.startswith("https://"),  # True on prod with HTTPS
        samesite="lax",
        max_age=int(access_expires.total_seconds()),
        path="/"
    )

    return {"access_token": jwt, "token_type": "bearer"}


# ===========================
# Logout (local / oauth)
# ===========================
@router.post("/logout")
def logout(request: Request, response: Response) -> Any:
    """
    Logout by blacklisting the bearer token (if present) and clearing cookie.
    Accepts either Authorization header or cookie.
    """
    token = None
    auth = request.headers.get("Authorization")
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    # fallback to cookie
    if not token:
        token = request.cookies.get("access_token")

    if token:
        sub = security.verify_token(token)
        ttl_seconds = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        blacklist_token(token, ttl_seconds)

    # Delete cookie on client
    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out successfully"}


# ===========================
# Forgot password & reset
# ===========================
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)) -> Any:
    email = request.email
    user_obj = crud_user.get_by_email(db, email=email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    reset_expires = timedelta(hours=1)
    reset_token = security.create_access_token(subject=str(user_obj.id), expires_delta=reset_expires)
    reset_link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?token={reset_token}"

    subject = "Password Reset Request"
    body = f"Hello {user_obj.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nThis link expires in 1 hour."

    try:
        send_email(subject, user_obj.email, body)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "Password reset email sent"}


@router.post("/reset-password")
def reset_password(token: str = Query(...), new_password: str = Query(...), db: Session = Depends(get_db)) -> Any:
    subject = security.verify_token(token)
    if not subject:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user_obj = crud_user.get(db, id=int(subject))
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    crud_user.update(db, db_obj=user_obj, obj_in={"password": new_password})
    return {"message": "Password reset successful"}


# ===========================
# OAuth: Google / Microsoft / GitHub
# ===========================
OAUTH_PROVIDERS = ["google", "microsoft", "github"]


@router.get("/oauth/{provider}")
async def oauth_login(provider: str) -> Any:
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider")

    state = secrets.token_urlsafe(32)
    save_oauth_state(state, provider, ttl_seconds=300)

    try:
        oauth_service = get_oauth_service(provider)
        auth_url = oauth_service.get_authorization_url(state)
        return {"authorization_url": auth_url, "provider": provider, "state": state}
    except Exception as e:
        logger.exception("Error building authorization URL for %s: %s", provider, e)
        pop_oauth_state(state)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error initiating OAuth: {str(e)}")


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported OAuth provider")

    if error:
        err_url = f"{settings.FRONTEND_URL.rstrip('/')}/login?error={error_description or error}"
        return RedirectResponse(url=err_url)

    if not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing state")
    saved_provider = get_oauth_state(state)
    if not saved_provider or saved_provider != provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OAuth state")
    pop_oauth_state(state)

    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing code parameter from provider")

    try:
        oauth_service = get_oauth_service(provider)

        # Exchange code
        token_data = await oauth_service.exchange_code_for_token(code)
        access_token = token_data.get("access_token") or token_data.get("token") or token_data.get("accessToken")
        if not access_token:
            raise Exception(f"No access_token in token response: {token_data}")

        # Get user info and create/find user
        user_info = await oauth_service.get_user_info(access_token)
        user_obj, created = oauth_service.find_or_create_user(user_info)

        # Create backend JWT
        jwt_token = oauth_service.create_jwt_token(user_obj)

        # Update last_login
        try:
            user_obj.last_login = datetime.utcnow()
            db.add(user_obj)
            db.commit()
        except Exception:
            db.rollback()

        oauth_service.close()

        # Build RedirectResponse and set cookie (delete existing first)
        # Redirect to frontend OAuth callback handler, which will then redirect to dashboard
        redirect_url = f"{settings.FRONTEND_URL.rstrip('/')}/auth/oauth/{provider}/callback"
        response = RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        # clear prior cookie (just in case)
        response.delete_cookie("access_token", path="/", domain=None)
        response.set_cookie(
            key="access_token",
            value=jwt_token["access_token"],
            httponly=True,
            secure=settings.FRONTEND_URL.startswith("https://"),
            samesite="lax",
            max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60),
            path="/",
            domain=None  # Let browser determine domain
        )
        return response

    except Exception as e:
        logger.exception("OAuth callback handling failed for %s: %s", provider, e)
        safe_error = quote(str(e))  # ✅ mã hoá chuỗi lỗi cho hợp lệ URL
        err_url = f"{settings.FRONTEND_URL.rstrip('/')}/login?error={safe_error}"
        return RedirectResponse(url=err_url)

@router.post("/oauth/logout")
def oauth_logout(request: Request, response: Response) -> Any:
    """
    Logout endpoint for OAuth users — accept cookie or Authorization header.
    """
    token = None
    auth = request.headers.get("Authorization")
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        token = request.cookies.get("access_token")

    if token:
        ttl_seconds = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        blacklist_token(token, ttl_seconds)

    response.delete_cookie("access_token", path="/")
    return {"message": "Logged out (OAuth) successfully"}
