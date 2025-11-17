"""
OAuth service for social login providers (Google, Microsoft, GitHub)
"""
import secrets
import httpx
from typing import Dict, Any, Tuple
from urllib.parse import urlencode

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token


class OAuthService:
    """Base OAuth service for all providers"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.config = self.get_provider_config(provider_name)
        self.db = SessionLocal()

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get OAuth configuration for provider"""
        configs = {
            "google": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile",
                "redirect_uri": f"{settings.OAUTH_BASE_URL}/api/v1/auth/oauth/google/callback",
            },
            "microsoft": {
                "client_id": settings.MICROSOFT_CLIENT_ID,
                "client_secret": settings.MICROSOFT_CLIENT_SECRET,
                "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "user_info_url": "https://graph.microsoft.com/v1.0/me",
                "scope": "openid email profile User.Read",
                "redirect_uri": f"{settings.OAUTH_BASE_URL}/api/v1/auth/oauth/microsoft/callback",
            },
            "github": {
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_info_url": "https://api.github.com/user",
                "scope": "read:user user:email",
                "redirect_uri": f"{settings.OAUTH_BASE_URL}/api/v1/auth/oauth/github/callback",
            },
        }
        return configs.get(provider, {})

    def get_authorization_url(self, state: str = None) -> str:
        """Generate authorization URL for redirect"""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "scope": self.config["scope"],
            "response_type": "code",
            "state": state,
        }
        return f"{self.config['authorize_url']}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config["redirect_uri"],
        }
        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.config["token_url"], data=data, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to exchange code: {response.text}")

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Generic user info fetch (overridden in child classes)"""
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.config["user_info_url"], headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()

    def find_or_create_user(self, oauth_data: Dict[str, Any]) -> Tuple[User, bool]:
        """Find user by oauth_id, or create new one"""

        # Google returns "sub", GitHub/Microsoft return "id"
        oauth_id = str(oauth_data.get("id") or oauth_data.get("sub"))
        email = oauth_data.get("email")

        existing_user = (
            self.db.query(User)
            .filter(
                User.oauth_provider == self.provider_name,
                User.oauth_id == oauth_id,
            )
            .first()
        )

        if existing_user:
            return existing_user, False

        existing_email_user = (
            self.db.query(User).filter(User.email == email).first() if email else None
        )

        if existing_email_user:
            # Link OAuth to existing account
            existing_email_user.oauth_provider = self.provider_name
            existing_email_user.oauth_id = oauth_id
            existing_email_user.oauth_email = email
            existing_email_user.oauth_avatar = oauth_data.get(
                "picture", oauth_data.get("avatar_url")
            )
            existing_email_user.is_oauth_account = True
            self.db.commit()
            return existing_email_user, False

        # Create new user
        username = email.split("@")[0] if email else f"{self.provider_name}_{oauth_id}"
        base_username = username
        counter = 1
        while self.db.query(User).filter(User.username == username).first():
            username = f"{base_username}_{counter}"
            counter += 1

        new_user = User(
            email=email or f"{username}@{self.provider_name}.com",
            username=username,
            hashed_password="",  # OAuth users don't need password
            full_name=oauth_data.get("name", oauth_data.get("login", username)),
            is_active=True,
            is_superuser=False,
            legacy_learning_goals=["general"],  # Fixed: use legacy_learning_goals instead
            difficulty_preference="medium",
            daily_study_time=30,
            oauth_provider=self.provider_name,
            oauth_id=oauth_id,
            oauth_email=email,
            oauth_avatar=oauth_data.get("picture", oauth_data.get("avatar_url")),
            is_oauth_account=True,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user, True

    def create_jwt_token(self, user: User) -> Dict[str, str]:
        access_token = create_access_token(subject=str(user.id))
        return {"access_token": access_token, "token_type": "bearer"}

    def close(self):
        if self.db:
            self.db.close()


# Provider-specific overrides
class GoogleOAuthService(OAuthService):
    def __init__(self):
        super().__init__("google")


class MicrosoftOAuthService(OAuthService):
    def __init__(self):
        super().__init__("microsoft")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(self.config["user_info_url"], headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get Microsoft user info: {response.text}")

        user_data = response.json()
        return {
            "id": user_data.get("id"),
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "name": user_data.get("displayName"),
            "picture": None,
        }


class GitHubOAuthService(OAuthService):
    def __init__(self):
        super().__init__("github")

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(self.config["user_info_url"], headers=headers)
            if profile_response.status_code != 200:
                raise Exception(f"Failed to get GitHub user info: {profile_response.text}")
            user_data = profile_response.json()

            # GitHub may not return email in profile
            emails_response = await client.get("https://api.github.com/user/emails", headers=headers)
            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next((e["email"] for e in emails if e.get("primary")), None)
                if primary_email:
                    user_data["email"] = primary_email

            return user_data


def get_oauth_service(provider: str) -> OAuthService:
    services = {
        "google": GoogleOAuthService,
        "microsoft": MicrosoftOAuthService,
        "github": GitHubOAuthService,
    }
    service_class = services.get(provider)
    if not service_class:
        raise ValueError(f"Unsupported OAuth provider: {provider}")
    return service_class()
