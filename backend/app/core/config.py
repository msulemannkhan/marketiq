from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Laptop Intelligence API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    # Environment
    ENVIRONMENT: str = "development"  # allowed: development, staging, production

    # Database
    DATABASE_URL: str
    db_port: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # LLM APIs
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str

    # Pinecone Vector Database
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX: str
    PINECONE_DIMENSION: int = 384  # For sentence-transformers/all-MiniLM-L6-v2

    # CORS
    CORS_ORIGINS: str = "*"  # Comma-separated list of origins or "*" for all

    # App settings
    DEBUG: bool = False
    LOAD_SAMPLE_DATA: bool = False
    backend_port: Optional[str] = None
    data_loader_port: Optional[str] = None

    # Security
    JWT_SECRET: Optional[str] = None
    SECRET_KEY: str 
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    jwt_algorithm: Optional[str] = None
    jwt_expiration_hours: Optional[str] = None

    # Password policy
    MIN_PASSWORD_LENGTH: int = 8
    MAX_PASSWORD_LENGTH: int = 128
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Security headers
    ENABLE_SECURITY_HEADERS: bool = True

    class Config:
        # Read from project root .env by default
        env_file = "../.env"


settings = Settings()

# If JWT_SECRET is provided, use it as SECRET_KEY for compatibility
if settings.JWT_SECRET:
    settings.SECRET_KEY = settings.JWT_SECRET