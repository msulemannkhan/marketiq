"""
Authentication core module providing user authentication and authorization utilities.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.core.config import settings
from app.core.security import security_scheme

# JWT Configuration (fallback values if not in settings)
JWT_SECRET = getattr(settings, 'SECRET_KEY', 'your-secret-key-here')
JWT_ALGORITHM = getattr(settings, 'ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 60) / 60  # Convert to hours


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """
    Verify JWT token and return user email.

    Args:
        credentials: HTTP Authorization credentials from request

    Returns:
        str: User email from token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(
    db: Session = Depends(get_db),
    email: str = Depends(verify_token)
) -> User:
    """
    Get current authenticated user from database.

    Args:
        db: Database session
        email: User email from verified JWT token

    Returns:
        User: Current authenticated user object

    Raises:
        HTTPException: If user not found in database
    """
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current authenticated and active user.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user object

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt