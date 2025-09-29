"""
Authentication endpoints with comprehensive security features.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import (
    security_scheme,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    rate_limiter,
    get_client_ip,
    SecurityHeaders,
    token_blacklist
)
from app.core.config import settings
from app.models.user import User, RefreshToken, LoginLog
from app.schemas.auth import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    UserSecurityInfo,
    LoginLogResponse,
    APIErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user with comprehensive validation"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked until {user.locked_until}",
            headers={"Retry-After": str(int((user.locked_until - datetime.utcnow()).total_seconds()))}
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (alias for clarity)"""
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


def log_login_attempt(
    db: Session,
    email: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    user_id: Optional[UUID] = None,
    failure_reason: Optional[str] = None
):
    """Log login attempt for security monitoring"""
    try:
        login_log = LoginLog(
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        db.add(login_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")
        db.rollback()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user with comprehensive validation"""
    client_ip = get_client_ip(request)

    # Rate limiting for registration
    rate_limit_key = f"register:{client_ip}"
    if rate_limiter.is_rate_limited(rate_limit_key, limit=5, window=3600):  # 5 registrations per hour
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later.",
            headers={"Retry-After": "3600"}
        )

    try:
        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            bio=user_data.bio,
            timezone=user_data.timezone,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Add security headers
        for key, value in SecurityHeaders.get_security_headers().items():
            response.headers[key] = value

        logger.info(f"User registered: {db_user.email} from IP {client_ip}")
        return db_user

    except IntegrityError as e:
        db.rollback()
        if "email" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )
        elif "username" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed due to constraint violation"
            )
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    # Rate limiting for login attempts
    rate_limit_key = f"login:{client_ip}"
    if rate_limiter.is_rate_limited(rate_limit_key, limit=10, window=900):  # 10 attempts per 15 minutes
        log_login_attempt(db, login_data.email, client_ip, user_agent, False, failure_reason="Rate limited")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": "900"}
        )

    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        log_login_attempt(db, login_data.email, client_ip, user_agent, False, failure_reason="User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        log_login_attempt(db, login_data.email, client_ip, user_agent, False, user.id, "Account locked")
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked until {user.locked_until}",
            headers={"Retry-After": str(int((user.locked_until - datetime.utcnow()).total_seconds()))}
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(hours=1)
            logger.warning(f"Account locked due to failed attempts: {user.email}")

        db.commit()
        log_login_attempt(db, login_data.email, client_ip, user_agent, False, user.id, "Invalid password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if user is active
    if not user.is_active:
        log_login_attempt(db, login_data.email, client_ip, user_agent, False, user.id, "Account deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if login_data.remember_me:
        access_token_expires = timedelta(days=7)  # Extended for "remember me"

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token_value = create_refresh_token(user.id)
    refresh_token_expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(refresh_token_value),
        expires_at=refresh_token_expires,
        device_info=user_agent[:500],
        ip_address=client_ip
    )

    db.add(refresh_token)
    db.commit()

    # Log successful login
    log_login_attempt(db, login_data.email, client_ip, user_agent, True, user.id)

    # Add security headers
    for key, value in SecurityHeaders.get_security_headers().items():
        response.headers[key] = value

    logger.info(f"User logged in: {user.email} from IP {client_ip}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value,
        expires_in=int(access_token_expires.total_seconds()),
        user=user
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    client_ip = get_client_ip(request)

    # Find refresh token
    refresh_tokens = db.query(RefreshToken).filter(RefreshToken.revoked_at.is_(None)).all()
    valid_token = None

    for token in refresh_tokens:
        if verify_password(refresh_data.refresh_token, token.token_hash):
            valid_token = token
            break

    if not valid_token or not valid_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user
    user = db.query(User).filter(User.id == valid_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    # Create new refresh token
    new_refresh_token_value = create_refresh_token(user.id)
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(new_refresh_token_value),
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        device_info=valid_token.device_info,
        ip_address=client_ip
    )

    # Revoke old refresh token
    valid_token.revoked_at = datetime.utcnow()

    db.add(new_refresh_token)
    db.commit()

    # Add security headers
    for key, value in SecurityHeaders.get_security_headers().items():
        response.headers[key] = value

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token_value,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )


@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    """Logout user and revoke tokens"""
    # Blacklist current access token
    token_payload = verify_token(credentials.credentials)
    if token_payload and token_payload.get("jti"):
        expires_at = datetime.fromtimestamp(token_payload["exp"])
        token_blacklist.blacklist_token(token_payload["jti"], expires_at)

    # Revoke refresh token
    refresh_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None)
    ).all()

    for token in refresh_tokens:
        if verify_password(refresh_data.refresh_token, token.token_hash):
            token.revoked_at = datetime.utcnow()
            break

    db.commit()
    logger.info(f"User logged out: {current_user.email}")

    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_sessions(
    current_user: User = Depends(get_current_active_user),
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    """Logout from all sessions and revoke all tokens"""
    # Blacklist current access token
    token_payload = verify_token(credentials.credentials)
    if token_payload and token_payload.get("jti"):
        expires_at = datetime.fromtimestamp(token_payload["exp"])
        token_blacklist.blacklist_token(token_payload["jti"], expires_at)

    # Revoke all refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.utcnow()})

    db.commit()
    logger.info(f"User logged out from all sessions: {current_user.email}")

    return {"message": "Successfully logged out from all sessions"}


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    update_data = user_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.email}")
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Hash new password
    new_hashed_password = get_password_hash(password_data.new_password)

    # Update password
    current_user.hashed_password = new_hashed_password
    current_user.password_changed_at = datetime.utcnow()
    current_user.updated_at = datetime.utcnow()

    # Revoke all refresh tokens to force re-login
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.utcnow()})

    db.commit()
    logger.info(f"Password changed for user: {current_user.email}")

    return {"message": "Password changed successfully. Please log in again."}


@router.get("/security", response_model=UserSecurityInfo)
async def get_security_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user security information"""
    # Get recent login attempts
    recent_logins = db.query(LoginLog).filter(
        LoginLog.email == current_user.email
    ).order_by(LoginLog.created_at.desc()).limit(10).all()

    # Count active sessions
    active_sessions = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None),
        RefreshToken.expires_at > datetime.utcnow()
    ).count()

    return UserSecurityInfo(
        failed_login_attempts=current_user.failed_login_attempts,
        locked_until=current_user.locked_until,
        password_changed_at=current_user.password_changed_at,
        last_login_at=current_user.last_login_at,
        recent_login_attempts=recent_logins,
        active_sessions=active_sessions
    )


@router.get("/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's active sessions"""
    sessions = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None),
        RefreshToken.expires_at > datetime.utcnow()
    ).order_by(RefreshToken.created_at.desc()).all()

    return [
        {
            "id": str(session.id),
            "created_at": session.created_at,
            "expires_at": session.expires_at,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "is_current": False  # Could be enhanced to detect current session
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    session = db.query(RefreshToken).filter(
        RefreshToken.id == session_id,
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None)
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    session.revoked_at = datetime.utcnow()
    db.commit()

    return {"message": "Session revoked successfully"}


# Health check for auth service
@router.get("/health")
async def auth_health_check():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "features": {
            "registration": True,
            "login": True,
            "token_refresh": True,
            "password_change": True,
            "session_management": True,
            "rate_limiting": rate_limiter.redis is not None,
            "token_blacklist": token_blacklist.redis is not None
        },
        "timestamp": datetime.utcnow()
    }