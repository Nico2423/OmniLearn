from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import secrets
import httpx

from app.core.config import settings
from app.models.user import User
from app.models.organization import OrganizationInvite
from app.schemas.user import UserCreate, UserOAuthCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_create: UserCreate) -> User:
    hashed_password = None
    if user_create.password:
        hashed_password = get_password_hash(user_create.password)
    
    db_user = User(
        email=user_create.email,
        name=user_create.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_oauth_user(db: Session, user_data: UserOAuthCreate) -> User:
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        google_id=user_data.google_id,
        avatar_url=user_data.avatar_url,
        last_login=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()


async def verify_google_token(token: str) -> Optional[dict]:
    """Verify Google OAuth token and return user info"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None


def generate_invite_token() -> str:
    """Generate a secure random token for organization invites"""
    return secrets.token_urlsafe(32)


def create_organization_invite(
    db: Session, 
    organization_id: int, 
    email: str, 
    role: str, 
    invited_by_id: int
) -> OrganizationInvite:
    """Create an organization invite"""
    token = generate_invite_token()
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days to accept
    
    invite = OrganizationInvite(
        organization_id=organization_id,
        email=email,
        role=role,
        invited_by_id=invited_by_id,
        token=token,
        expires_at=expires_at
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def get_invite_by_token(db: Session, token: str) -> Optional[OrganizationInvite]:
    """Get organization invite by token"""
    return db.query(OrganizationInvite).filter(
        OrganizationInvite.token == token,
        OrganizationInvite.expires_at > datetime.utcnow(),
        OrganizationInvite.accepted_at.is_(None)
    ).first()