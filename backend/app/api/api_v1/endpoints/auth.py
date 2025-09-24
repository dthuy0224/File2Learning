from datetime import datetime, timedelta
from typing import Any, Dict
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.crud import user
from app.schemas.token import Token
from app.schemas.user import User
from app.core import deps
from app.services.oauth_service import get_oauth_service

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user_obj = user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user_obj.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/test-token", response_model=User)
def test_token(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    return current_user


# OAuth Providers
OAUTH_PROVIDERS = ["google", "microsoft", "github"]

@router.get("/oauth/{provider}")
async def oauth_login(provider: str) -> Any:
    """
    Initiate OAuth login with provider
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    try:
        oauth_service = get_oauth_service(provider)
        auth_url = oauth_service.get_authorization_url(state)

        # Store state in session/cookie for validation later
        # For now, we'll validate state in callback

        return {
            "authorization_url": auth_url,
            "provider": provider,
            "state": state
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating OAuth: {str(e)}"
        )


@router.get("/{provider}/callback", response_model=Token)
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Handle OAuth callback from provider
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error_description or error}"
        )

    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )

    try:
        oauth_service = get_oauth_service(provider)

        # Exchange code for access token
        token_data = await oauth_service.exchange_code_for_token(code)

        # Get user info from provider
        user_info = await oauth_service.get_user_info(token_data['access_token'])

        # Find or create user
        user_obj, is_created = oauth_service.find_or_create_user(user_info)

        # Create JWT token
        jwt_token = oauth_service.create_jwt_token(user_obj)

        # Update last login
        user_obj.last_login = datetime.utcnow()
        db.commit()

        # Close database connection
        oauth_service.close()

        # Redirect to frontend with token as query parameter
        frontend_callback_url = f"http://localhost:3000/auth/{provider}/callback?token={jwt_token['access_token']}"
        return RedirectResponse(url=frontend_callback_url)

    except Exception as e:
        # Redirect to frontend with error
        error_url = f"http://localhost:3000/login?error={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/oauth-urls")
async def get_oauth_urls() -> Dict[str, Any]:
    urls = {}

    for provider in OAUTH_PROVIDERS:
        try:
            oauth_service = get_oauth_service(provider)
            auth_url = oauth_service.get_authorization_url()
            urls[provider] = {
                "authorization_url": auth_url,
                "provider": provider
            }
        except Exception as e:
            urls[provider] = {"error": str(e)}

    return {"oauth_urls": urls}
