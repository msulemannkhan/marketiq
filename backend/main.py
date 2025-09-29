"""
Review Intelligence System API - Main Entry Point
Force reload: v10
"""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Import configuration
from app.core.config import settings
from app.core.database import engine, Base

# Import API router
from app.api.v1.api import api_router

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    logger.info("Starting Review Intelligence System API...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Load sample data if configured
    if settings.LOAD_SAMPLE_DATA:
        try:
            from app.core.data_loader import load_sample_data
            from app.core.database import SessionLocal
            db = SessionLocal()
            load_sample_data(db)
            db.close()
            logger.info("Sample data loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down Review Intelligence System API...")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS and settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info("API router mounted with all modular endpoints")

# Root-level health endpoints for environments that probe /health directly
@app.get("/health")
async def root_health():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/")
async def root_info():
    return {"message": "Review Intelligence System API", "version": settings.VERSION, "status": "operational"}

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )