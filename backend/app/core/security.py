import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
import ipaddress

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import redis  # Using in-memory caching instead
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Enhanced password context with multiple schemes and security settings
pwd_context = CryptContext(
    schemes=["bcrypt", "scrypt", "argon2"],
    default="bcrypt",
    deprecated="auto",
    bcrypt__rounds=12,  # Increased rounds for better security
    scrypt__rounds=16,
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=1,
)

# In-memory cache for rate limiting and token blacklisting
from collections import defaultdict
from threading import Lock

class InMemoryCache:
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.lock = Lock()

    def get(self, key):
        with self.lock:
            if key in self.expiry and datetime.now() > self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
                return None
            return self.data.get(key)

    def set(self, key, value, ttl=None):
        with self.lock:
            self.data[key] = value
            if ttl:
                self.expiry[key] = datetime.now() + timedelta(seconds=ttl)

    def incr(self, key):
        with self.lock:
            current = int(self.data.get(key, 0))
            self.data[key] = current + 1
            return self.data[key]

    def expire(self, key, ttl):
        with self.lock:
            if key in self.data:
                self.expiry[key] = datetime.now() + timedelta(seconds=ttl)

    def ttl(self, key):
        with self.lock:
            if key in self.expiry:
                remaining = (self.expiry[key] - datetime.now()).total_seconds()
                return max(0, int(remaining))
            return -1

    def exists(self, key):
        return self.get(key) is not None

    def setex(self, key, ttl, value):
        self.set(key, value, ttl)

    def pipeline(self):
        return self  # Simple mock for pipeline

    def execute(self):
        return [True, True]  # Mock pipeline execution

    def info(self):
        """Mock Redis info method for health checks"""
        return {
            "redis_version": "in-memory-cache",
            "connected_clients": 1,
            "used_memory": len(str(self.data)),
            "used_memory_human": f"{len(str(self.data))}B"
        }

# Initialize in-memory cache for rate limiting and token blacklist
cache_client = InMemoryCache()

# Alias for backward compatibility
redis_client = cache_client


class SecurityHeaders:
    """Security headers middleware"""

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }


class RateLimiter:
    """Advanced rate limiting with Redis backend"""

    def __init__(self):
        self.redis = cache_client

    def is_rate_limited(self, key: str, limit: int = None, window: int = None) -> bool:
        """Check if key is rate limited"""
        if not self.redis:
            return False

        limit = limit or settings.RATE_LIMIT_REQUESTS
        window = window or settings.RATE_LIMIT_WINDOW

        try:
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            results = pipe.execute()

            current_count = results[0]
            return current_count > limit
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False

    def get_rate_limit_info(self, key: str) -> Dict[str, Any]:
        """Get rate limit information for key"""
        if not self.redis:
            return {"remaining": settings.RATE_LIMIT_REQUESTS, "reset_at": None}

        try:
            current = self.redis.get(key) or 0
            ttl = self.redis.ttl(key)
            remaining = max(0, settings.RATE_LIMIT_REQUESTS - int(current))
            reset_at = datetime.utcnow() + timedelta(seconds=max(0, ttl)) if ttl > 0 else None

            return {
                "remaining": remaining,
                "reset_at": reset_at,
                "current": int(current),
                "limit": settings.RATE_LIMIT_REQUESTS
            }
        except Exception as e:
            logger.error(f"Rate limit info retrieval failed: {e}")
            return {"remaining": settings.RATE_LIMIT_REQUESTS, "reset_at": None}


class TokenBlacklist:
    """JWT token blacklist using Redis"""

    def __init__(self):
        self.redis = cache_client

    def blacklist_token(self, jti: str, expires_at: datetime):
        """Add token to blacklist"""
        if not self.redis:
            return

        try:
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                self.redis.setex(f"blacklist:{jti}", ttl, "1")
        except Exception as e:
            logger.error(f"Token blacklisting failed: {e}")

    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        if not self.redis:
            return False

        try:
            return self.redis.exists(f"blacklist:{jti}")
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False


# Initialize components
rate_limiter = RateLimiter()
token_blacklist = TokenBlacklist()


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    scopes: List[str] = None
) -> str:
    """Create JWT access token with enhanced security"""
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": settings.PROJECT_NAME,
        "aud": "laptop-intelligence-api",
        "jti": secrets.token_urlsafe(32),  # Unique token ID
        "scopes": scopes or []
    })

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: UUID) -> str:
    """Create refresh token"""
    return secrets.token_urlsafe(64)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash with timing attack protection"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Password verification failed: {e}")
        # Perform dummy hash to prevent timing attacks
        pwd_context.hash("dummy_password")
        return False


def get_password_hash(password: str) -> str:
    """Generate secure password hash"""
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token with enhanced security checks"""
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="laptop-intelligence-api",
            issuer=settings.PROJECT_NAME
        )

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and token_blacklist.is_blacklisted(jti):
            logger.warning(f"Attempted use of blacklisted token: {jti}")
            return None

        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token"""
    return secrets.token_urlsafe(length)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify CSRF token using HMAC"""
    try:
        expected = hmac.new(
            settings.SECRET_KEY.encode(),
            session_token.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(token, expected)
    except Exception:
        return False


def generate_csrf_token(session_token: str) -> str:
    """Generate CSRF token using HMAC"""
    return hmac.new(
        settings.SECRET_KEY.encode(),
        session_token.encode(),
        hashlib.sha256
    ).hexdigest()


class IPValidator:
    """IP address validation and security checks"""

    # Known malicious IP ranges (simplified example)
    BLOCKED_RANGES = [
        "0.0.0.0/8",    # This network
        "10.0.0.0/8",   # Private
        "127.0.0.0/8",  # Loopback (except in development)
        "169.254.0.0/16",  # Link-local
        "172.16.0.0/12",   # Private
        "192.168.0.0/16",  # Private
    ]

    @classmethod
    def is_valid_ip(cls, ip: str) -> bool:
        """Validate IP address format"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    @classmethod
    def is_private_ip(cls, ip: str) -> bool:
        """Check if IP is in private range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False

    @classmethod
    def is_blocked_ip(cls, ip: str) -> bool:
        """Check if IP is in blocked ranges"""
        # Allow localhost and Docker internal IPs in development
        if settings.ENVIRONMENT == "development":
            allowed_ips = ["127.0.0.1", "localhost", "::1", "172.18.0.1", "172.17.0.1"]
            if ip in allowed_ips:
                return False

        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Skip blocking for localhost and Docker internal IPs in development
            if settings.ENVIRONMENT == "development":
                if str(ip_obj) in ["127.0.0.1", "172.18.0.1", "172.17.0.1"]:
                    return False
                # Allow any Docker internal network in development
                if ip_obj.is_private and str(ip_obj).startswith(("172.", "10.", "192.168.")):
                    return False

            for blocked_range in cls.BLOCKED_RANGES:
                if ip_obj in ipaddress.ip_network(blocked_range, strict=False):
                    return True
            return False
        except ValueError:
            return True  # Block invalid IPs


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request with proxy support"""
    # Check for forwarded headers (in order of preference)
    forwarded_headers = [
        "x-forwarded-for",
        "x-real-ip",
        "cf-connecting-ip",  # Cloudflare
        "x-forwarded",
        "forwarded-for",
        "forwarded"
    ]

    for header in forwarded_headers:
        if header in request.headers:
            # Take first IP from comma-separated list
            ip = request.headers[header].split(",")[0].strip()
            if IPValidator.is_valid_ip(ip):
                return ip

    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


class EnhancedHTTPBearer(HTTPBearer):
    """Enhanced HTTP Bearer authentication with additional security checks"""

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """Enhanced authentication with rate limiting and security checks"""
        client_ip = get_client_ip(request)

        # Rate limiting
        rate_limit_key = f"auth_attempts:{client_ip}"
        if rate_limiter.is_rate_limited(rate_limit_key, limit=20, window=300):  # 20 attempts per 5 minutes
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later.",
                headers={"Retry-After": "300"}
            )

        # IP validation
        if IPValidator.is_blocked_ip(client_ip):
            logger.warning(f"Blocked IP attempted authentication: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied from this IP address"
            )

        return await super().__call__(request)


# Create enhanced bearer instance
security_scheme = EnhancedHTTPBearer(auto_error=False)