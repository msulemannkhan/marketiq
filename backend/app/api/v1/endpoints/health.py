"""
Comprehensive health check endpoints with detailed system monitoring.
"""

import asyncio
import logging
import time
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
import httpx

from ....core.database import get_db, engine
from ....core.config import settings
from ....core.security import redis_client, rate_limiter
from ....models.product import Product
from ....models.variant import Variant
from ....models.user import User, LoginLog
from ....services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthChecker:
    """Comprehensive health checking service"""

    @staticmethod
    async def check_database(db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        start_time = time.time()
        try:
            # Test basic connectivity
            db.execute(text("SELECT 1"))

            # Get connection info
            result = db.execute(text("SELECT version()")).fetchone()
            db_version = result[0] if result else "Unknown"

            # Check table counts
            product_count = db.query(Product).count()
            variant_count = db.query(Variant).count()
            user_count = db.query(User).count()

            # Check recent activity
            recent_logins = db.query(LoginLog).filter(
                LoginLog.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()

            response_time = (time.time() - start_time) * 1000  # ms

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "version": db_version,
                "statistics": {
                    "products": product_count,
                    "variants": variant_count,
                    "users": user_count,
                    "recent_logins_24h": recent_logins
                },
                "performance": {
                    "query_time_ms": round(response_time, 2),
                    "status": "good" if response_time < 100 else "slow" if response_time < 500 else "critical"
                }
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        if not redis_client:
            return {
                "status": "not_configured",
                "message": "Redis is not configured"
            }

        start_time = time.time()
        try:
            # Test connectivity
            info = redis_client.info()

            # Test read/write
            test_key = f"health_check:{int(time.time())}"
            redis_client.set(test_key, "test", ex=60)
            value = redis_client.get(test_key)
            redis_client.delete(test_key)

            if value != "test":
                raise Exception("Read/write test failed")

            response_time = (time.time() - start_time) * 1000  # ms

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "info": {
                    "version": info.get("redis_version", "Unknown"),
                    "memory_used": info.get("used_memory_human", "Unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "uptime_seconds": info.get("uptime_in_seconds", 0)
                },
                "performance": {
                    "response_time_ms": round(response_time, 2),
                    "status": "good" if response_time < 10 else "slow" if response_time < 50 else "critical"
                }
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }

    @staticmethod
    async def check_llm_service() -> Dict[str, Any]:
        """Check LLM service connectivity and configuration"""
        if not settings.GEMINI_API_KEY:
            return {
                "status": "not_configured",
                "message": "LLM service is not configured (missing API key)"
            }

        start_time = time.time()
        try:
            # Test LLM service
            llm_service = LLMService()
            test_response = await llm_service.simple_query("Test connection")

            response_time = (time.time() - start_time) * 1000  # ms

            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "provider": "Google Gemini",
                "test_successful": bool(test_response),
                "performance": {
                    "response_time_ms": round(response_time, 2),
                    "status": "good" if response_time < 2000 else "slow" if response_time < 5000 else "critical"
                }
            }
        except Exception as e:
            logger.error(f"LLM service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": (time.time() - start_time) * 1000
            }

    @staticmethod
    async def check_external_dependencies() -> Dict[str, Any]:
        """Check external service dependencies"""
        dependencies = {}

        # Test external HTTP services (if any)
        external_services = [
            # Add any external services your app depends on
            # {"name": "example_api", "url": "https://api.example.com/health"}
        ]

        for service in external_services:
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(service["url"])
                    response_time = (time.time() - start_time) * 1000

                    dependencies[service["name"]] = {
                        "status": "healthy" if response.status_code == 200 else "unhealthy",
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time, 2)
                    }
            except Exception as e:
                dependencies[service["name"]] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "response_time_ms": (time.time() - start_time) * 1000
                }

        return dependencies

    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage('/')

            # System info
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": cpu_count,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }

            return {
                "status": "healthy",
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "status": "good" if cpu_percent < 70 else "warning" if cpu_percent < 90 else "critical"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "good" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "status": "good" if disk.free > 5*(1024**3) else "warning" if disk.free > 1*(1024**3) else "critical"
                },
                "system": system_info
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def check_rate_limiting() -> Dict[str, Any]:
        """Check rate limiting functionality"""
        if not rate_limiter.redis:
            return {
                "status": "disabled",
                "message": "Rate limiting is disabled (Redis not available)"
            }

        try:
            # Test rate limiting functionality
            test_key = f"health_test:{int(time.time())}"
            is_limited = rate_limiter.is_rate_limited(test_key, limit=1, window=60)
            rate_info = rate_limiter.get_rate_limit_info(test_key)

            return {
                "status": "healthy",
                "functional": True,
                "test_result": {
                    "first_request_limited": is_limited,
                    "rate_info": rate_info
                }
            }
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


health_checker = HealthChecker()


@router.get("/")
async def root_endpoint():
    """Root API endpoint"""
    return {
        "message": "Review Intelligence System API",
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health")
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Laptop Intelligence API",
        "version": settings.VERSION
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check with all system components"""
    start_time = time.time()

    # Run all health checks concurrently
    checks = await asyncio.gather(
        health_checker.check_database(db),
        health_checker.check_redis(),
        health_checker.check_llm_service(),
        health_checker.check_external_dependencies(),
        return_exceptions=True
    )

    database_health, redis_health, llm_health, external_deps = checks

    # System resource check (synchronous)
    system_health = health_checker.check_system_resources()
    rate_limiting_health = health_checker.check_rate_limiting()

    total_time = (time.time() - start_time) * 1000

    # Determine overall status
    component_statuses = [
        database_health.get("status"),
        redis_health.get("status"),
        llm_health.get("status"),
        system_health.get("status"),
        rate_limiting_health.get("status")
    ]

    if "unhealthy" in component_statuses:
        overall_status = "unhealthy"
    elif "not_configured" in component_statuses or "disabled" in component_statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "total_check_time_ms": round(total_time, 2),
        "components": {
            "database": database_health,
            "redis": redis_health,
            "llm_service": llm_health,
            "system_resources": system_health,
            "rate_limiting": rate_limiting_health,
            "external_dependencies": external_deps
        },
        "service_info": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": "production" if "production" in settings.DATABASE_URL else "development",
            "uptime_check": "basic"  # Could be enhanced with actual uptime tracking
        }
    }


@router.get("/database")
async def database_health_check(db: Session = Depends(get_db)):
    """Database-specific health check"""
    result = await health_checker.check_database(db)

    if result["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database is {result['status']}: {result.get('error', 'Unknown error')}"
        )

    return result


@router.get("/redis")
async def redis_health_check():
    """Redis-specific health check"""
    result = await health_checker.check_redis()

    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis is {result['status']}: {result.get('error', 'Unknown error')}"
        )

    return result


@router.get("/llm")
async def llm_health_check():
    """LLM service-specific health check"""
    result = await health_checker.check_llm_service()

    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service is {result['status']}: {result.get('error', 'Unknown error')}"
        )

    return result


@router.get("/system")
async def system_health_check():
    """System resources health check"""
    result = health_checker.check_system_resources()

    # Check for critical resource usage
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"System health check failed: {result.get('error', 'Unknown error')}"
        )

    # Check for critical resource thresholds
    critical_issues = []

    if result.get("cpu", {}).get("status") == "critical":
        critical_issues.append("CPU usage is critical")

    if result.get("memory", {}).get("status") == "critical":
        critical_issues.append("Memory usage is critical")

    if result.get("disk", {}).get("status") == "critical":
        critical_issues.append("Disk space is critical")

    if critical_issues:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Critical system issues: {'; '.join(critical_issues)}"
        )

    return result


@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes-style readiness probe"""
    # Check essential services for readiness
    checks = await asyncio.gather(
        health_checker.check_database(db),
        health_checker.check_redis(),
        return_exceptions=True
    )

    database_health, redis_health = checks

    # For readiness, we need database to be healthy
    if database_health.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready: database unavailable"
        )

    # Redis is nice to have but not critical for readiness
    redis_status = redis_health.get("status", "unknown")

    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "pass",
            "redis": "pass" if redis_status in ["healthy", "not_configured"] else "warn"
        }
    }


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    # Basic liveness check - just verify the app is responding
    try:
        # Simple check that doesn't depend on external resources
        current_time = datetime.utcnow()

        return {
            "status": "alive",
            "timestamp": current_time.isoformat(),
            "uptime_check": "pass"
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not alive"
        )


@router.get("/metrics")
async def health_metrics(db: Session = Depends(get_db)):
    """Health metrics for monitoring systems"""
    start_time = time.time()

    # Gather metrics
    try:
        # Database metrics
        db_start = time.time()
        product_count = db.query(Product).count()
        variant_count = db.query(Variant).count()
        user_count = db.query(User).count()
        db_time = (time.time() - db_start) * 1000

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        # Redis metrics (if available)
        redis_metrics = {}
        if redis_client:
            try:
                info = redis_client.info()
                redis_metrics = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            except Exception:
                redis_metrics = {"status": "error"}

        total_time = (time.time() - start_time) * 1000

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "collection_time_ms": round(total_time, 2),
            "database": {
                "query_time_ms": round(db_time, 2),
                "counts": {
                    "products": product_count,
                    "variants": variant_count,
                    "users": user_count
                }
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2)
            },
            "redis": redis_metrics,
            "service": {
                "version": settings.VERSION,
                "name": settings.PROJECT_NAME
            }
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
        )