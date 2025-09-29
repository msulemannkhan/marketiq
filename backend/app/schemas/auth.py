"""
Authentication and authorization schemas.
"""

import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from uuid import UUID

from ..core.config import settings


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    timezone: str = Field(default="UTC", max_length=50)

    @field_validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.lower()

    @field_validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower()


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH, max_length=settings.MAX_PASSWORD_LENGTH)
    password_confirm: str

    @field_validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength according to policy"""
        errors = []

        if len(v) < settings.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long")

        if len(v) > settings.MAX_PASSWORD_LENGTH:
            errors.append(f"Password must be at most {settings.MAX_PASSWORD_LENGTH} characters long")

        if settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")

        if settings.REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")

        if settings.REQUIRE_NUMBERS and not re.search(r'\d', v):
            errors.append("Password must contain at least one number")

        if settings.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")

        if errors:
            raise ValueError("; ".join(errors))

        return v

    @model_validator(mode='before')
    def validate_password_match(cls, values):
        """Validate password confirmation matches"""
        password = values.get('password')
        password_confirm = values.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValueError('Passwords do not match')

        return values


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    timezone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserResponse(UserBase):
    """Schema for user response"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile schema"""
    updated_at: datetime
    email_verified_at: Optional[datetime]
    preferences: Optional[dict] = {}

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = Field(default=False)

    @field_validator('email')
    def validate_email(cls, v):
        return v.lower()


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class TokenData(BaseModel):
    """Token data schema for internal use"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    scopes: List[str] = []


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH, max_length=settings.MAX_PASSWORD_LENGTH)
    new_password_confirm: str

    @field_validator('new_password')
    def validate_password_strength(cls, v):
        """Validate new password strength"""
        errors = []

        if len(v) < settings.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long")

        if settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")

        if settings.REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")

        if settings.REQUIRE_NUMBERS and not re.search(r'\d', v):
            errors.append("Password must contain at least one number")

        if settings.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")

        if errors:
            raise ValueError("; ".join(errors))

        return v

    @model_validator(mode='before')
    def validate_password_match(cls, values):
        """Validate new password confirmation matches"""
        new_password = values.get('new_password')
        new_password_confirm = values.get('new_password_confirm')

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValueError('New passwords do not match')

        return values


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr

    @field_validator('email')
    def validate_email(cls, v):
        return v.lower()


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH, max_length=settings.MAX_PASSWORD_LENGTH)
    new_password_confirm: str

    @field_validator('new_password')
    def validate_password_strength(cls, v):
        """Validate new password strength"""
        errors = []

        if len(v) < settings.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters long")

        if settings.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', v):
            errors.append("Password must contain at least one uppercase letter")

        if settings.REQUIRE_LOWERCASE and not re.search(r'[a-z]', v):
            errors.append("Password must contain at least one lowercase letter")

        if settings.REQUIRE_NUMBERS and not re.search(r'\d', v):
            errors.append("Password must contain at least one number")

        if settings.REQUIRE_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            errors.append("Password must contain at least one special character")

        if errors:
            raise ValueError("; ".join(errors))

        return v

    @model_validator(mode='before')
    def validate_password_match(cls, values):
        """Validate new password confirmation matches"""
        new_password = values.get('new_password')
        new_password_confirm = values.get('new_password_confirm')

        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValueError('New passwords do not match')

        return values


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    email: EmailStr

    @field_validator('email')
    def validate_email(cls, v):
        return v.lower()


class EmailVerificationConfirm(BaseModel):
    """Email verification confirmation schema"""
    token: str


class LoginLogResponse(BaseModel):
    """Login log response schema"""
    id: UUID
    email: str
    ip_address: str
    user_agent: Optional[str]
    success: bool
    failure_reason: Optional[str]
    created_at: datetime
    country: Optional[str]
    city: Optional[str]

    class Config:
        from_attributes = True


class UserSecurityInfo(BaseModel):
    """User security information schema"""
    failed_login_attempts: int
    locked_until: Optional[datetime]
    password_changed_at: datetime
    last_login_at: Optional[datetime]
    recent_login_attempts: List[LoginLogResponse]
    active_sessions: int

    class Config:
        from_attributes = True


class APIErrorResponse(BaseModel):
    """Standard API error response schema"""
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime
    path: Optional[str] = None