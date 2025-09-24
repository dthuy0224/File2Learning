"""
OAuth service for social login providers (Google, Microsoft, GitHub)
"""
import secrets
import httpx
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, urljoin

from app.core.config import settings
from app.core.database import SessionLocal
from app.crud.crud_user import user as user_crud
from app.core.security import create_access_token
from app.models.user import User


class OAuthService:
    """Base OAuth service for all providers"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.config = self.get_provider_config(provider_name)
        self.db = SessionLocal()

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get OAuth configuration for provider"""
        configs = {
            'google': {
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile',
                'redirect_uri': f"{settings.OAUTH_BASE_URL}/api/v1/auth/google/callback"
            },
            'microsoft': {
                'client_id': settings.MICROSOFT_CLIENT_ID,
                'client_secret': settings.MICROSOFT_CLIENT_SECRET,
                'authorize_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'user_info_url': 'https://graph.microsoft.com/v1.0/me',
                'scope': 'openid email profile User.Read',
                'redirect_uri': f"{settings.OAUTH_BASE_URL}/api/v1/auth/microsoft/callback"
            },
            'github': {
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'authorize_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'scope': 'user:email',
                'redirect_uri': f"{settings.OAUTH_BASE_URL}/api/v1/auth/github/callback"
            }
        }
        return configs.get(provider, {})

    def get_authorization_url(self, state: str = None) -> str:
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.config['client_id'],
            'redirect_uri': self.config['redirect_uri'],
            'scope': self.config['scope'],
            'response_type': 'code',
            'state': state
        }

        url = f"{self.config['authorize_url']}?{urlencode(params)}"
        return url

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.config['redirect_uri']
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.config['token_url'], data=data)

        if response.status_code != 200:
            raise Exception(f"Failed to exchange code: {response.text}")

        return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from OAuth provider"""
        headers = {'Authorization': f'Bearer {access_token}'}

        # Special handling for GitHub (uses different auth method)
        if self.provider_name == 'github':
            headers['Accept'] = 'application/vnd.github.v3+json'

        async with httpx.AsyncClient() as client:
            response = await client.get(self.config['user_info_url'], headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")

        return response.json()

    def find_or_create_user(self, oauth_data: Dict[str, Any]) -> Tuple[User, bool]:
        # Check if user exists by OAuth provider and ID
        existing_user = self.db.query(User).filter(
            User.oauth_provider == self.provider_name,
            User.oauth_id == str(oauth_data['id'])
        ).first()

        if existing_user:
            return existing_user, False  # User exists, not created

        # Check if email already exists (link accounts)
        email = oauth_data.get('email')
        if email:
            existing_email_user = self.db.query(User).filter(User.email == email).first()
        else:
            existing_email_user = None

        if existing_email_user:
            # Link OAuth to existing account
            existing_email_user.oauth_provider = self.provider_name
            existing_email_user.oauth_id = str(oauth_data['id'])
            existing_email_user.oauth_email = email
            existing_email_user.oauth_avatar = oauth_data.get('picture', oauth_data.get('avatar_url'))
            existing_email_user.is_oauth_account = True
            self.db.commit()
            return existing_email_user, False

        # Create new user
        username = oauth_data.get('email', f"{self.provider_name}_{oauth_data['id']}")
        if '@' in username:
            username = username.split('@')[0]

        # Ensure unique username
        counter = 1
        original_username = username
        while self.db.query(User).filter(User.username == username).first():
            username = f"{original_username}_{counter}"
            counter += 1

        new_user = User(
            email=email or f"{username}@{self.provider_name}.com",
            username=username,
            hashed_password="",  # OAuth users don't have passwords
            full_name=oauth_data.get('name', oauth_data.get('login', username)),
            is_active=True,
            is_superuser=False,
            learning_goals=['general'],
            difficulty_preference='medium',
            daily_study_time=30,
            oauth_provider=self.provider_name,
            oauth_id=str(oauth_data['id']),
            oauth_email=email,
            oauth_avatar=oauth_data.get('picture', oauth_data.get('avatar_url')),
            is_oauth_account=True
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user, True  # User created

    def create_jwt_token(self, user: User) -> Dict[str, str]:
        access_token = create_access_token(subject=str(user.id))
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()


class GoogleOAuthService(OAuthService):
    """Google OAuth service"""

    def __init__(self):
        super().__init__('google')

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Google"""
        headers = {'Authorization': f'Bearer {access_token}'}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.config['user_info_url'], headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get Google user info: {response.text}")

        user_data = response.json()

        # Get email if not included in basic profile
        if 'email' not in user_data:
            email_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers,
                params={'fields': 'email'}
            )
            if email_response.status_code == 200:
                email_data = email_response.json()
                user_data['email'] = email_data.get('email')

        return user_data


class MicrosoftOAuthService(OAuthService):
    def __init__(self):
        super().__init__('microsoft')
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.config['user_info_url'], headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get Microsoft user info: {response.text}")

        user_data = response.json()

        # Microsoft returns different field names
        return {
            'id': user_data.get('id'),
            'email': user_data.get('mail') or user_data.get('userPrincipalName'),
            'name': user_data.get('displayName'),
            'picture': None  
        }


class GitHubOAuthService(OAuthService):
    def __init__(self):
        super().__init__('github')

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from GitHub"""
        headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        async with httpx.AsyncClient() as client:
            # Get user profile
            profile_response = await client.get(self.config['user_info_url'], headers=headers)
            if profile_response.status_code != 200:
                raise Exception(f"Failed to get GitHub user info: {profile_response.text}")

            user_data = profile_response.json()

            emails_response = await client.get(
                'https://api.github.com/user/emails',
                headers=headers
            )

            if emails_response.status_code == 200:
                emails = emails_response.json()
                primary_email = next((email['email'] for email in emails if email['primary']), None)
                user_data['email'] = primary_email or user_data.get('email')

            return user_data


def get_oauth_service(provider: str) -> OAuthService:
    services = {
        'google': GoogleOAuthService,
        'microsoft': MicrosoftOAuthService,
        'github': GitHubOAuthService
    }

    service_class = services.get(provider)
    if not service_class:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    return service_class()
