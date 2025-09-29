from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
api_router = APIRouter()

# Import all endpoint modules
try:
    # Authentication & Security
    from app.api.v1.endpoints.auth import router as auth_router

    # Product Management
    from app.api.v1.endpoints.catalog import router as catalog_router
    # from app.api.v1.endpoints.offers import router as offers_router
    from app.api.v1.endpoints.product_qa import router as product_qa_router
    from app.api.v1.endpoints.price_history import router as price_history_router

    # Reviews Management
    from app.api.v1.endpoints.reviews import router as reviews_router
    from app.api.v1.endpoints.reviews_analytics import router as reviews_analytics_router
    # from app.api.v1.endpoints.review_analytics import router as review_analytics_router

    # Search & Filter
    from app.api.v1.endpoints.search import router as search_router
    from app.api.v1.endpoints.compare import router as compare_router

    # AI & Chat
    from app.api.v1.endpoints.chat import router as chat_router
    from app.api.v1.endpoints.recommendations import router as recommendations_router
    from app.api.v1.endpoints.enhanced_recommendations import router as enhanced_recommendations_router

    # Analytics & Dashboard
    from app.api.v1.endpoints.analytics import router as analytics_router
    from app.api.v1.endpoints.dashboard import router as dashboard_router

    # System & Admin
    from app.api.v1.endpoints.health import router as health_router
    from app.api.v1.endpoints.admin import router as admin_router
    from app.api.v1.endpoints.data_import import router as data_import_router

    ENDPOINTS_LOADED = True
    logger.info("✅ All endpoint modules loaded successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import endpoints: {e}")
    ENDPOINTS_LOADED = False

# Mount endpoints in organized sections
if ENDPOINTS_LOADED:
    # ===== AUTHENTICATION & SECURITY =====
    api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

    # ===== PRODUCT MANAGEMENT =====
    # Core product endpoints
    api_router.include_router(catalog_router, prefix="/products", tags=["Products"])

    # Product offers endpoints
    # api_router.include_router(offers_router, prefix="/products", tags=["Product Offers"])

    # Product Q&A endpoints
    api_router.include_router(product_qa_router, prefix="/products", tags=["Product Q&A"])

    # Price history endpoints
    api_router.include_router(price_history_router, prefix="/products", tags=["Price History"])

    # ===== REVIEWS MANAGEMENT =====
    api_router.include_router(reviews_router, prefix="", tags=["Reviews"])  # Root level since routes have /reviews
    api_router.include_router(reviews_analytics_router, prefix="/reviews", tags=["Reviews Analytics"])
    # api_router.include_router(review_analytics_router, prefix="/reviews", tags=["Review Analytics"])

    # ===== SEARCH & DISCOVERY =====
    api_router.include_router(search_router, prefix="", tags=["Search"])  # Root level since routes have /search
    api_router.include_router(compare_router, prefix="", tags=["Product Comparison"])

    # ===== AI & INTELLIGENCE =====
    api_router.include_router(chat_router, prefix="", tags=["Chat"])  # Root level since routes have /chat
    api_router.include_router(recommendations_router, prefix="", tags=["Recommendations"])  # Root level since routes have /recommendations
    api_router.include_router(enhanced_recommendations_router, prefix="/ai", tags=["AI Enhanced"])

    # ===== ANALYTICS & DASHBOARD =====
    api_router.include_router(analytics_router, prefix="", tags=["Analytics"])  # Routes already have /analytics
    api_router.include_router(dashboard_router, prefix="", tags=["Dashboard"])  # Routes already have /dashboard

    # ===== SYSTEM & ADMIN =====
    api_router.include_router(health_router, prefix="", tags=["System"])  # Root level for /api/v1/health and root
    api_router.include_router(admin_router, prefix="/admin", tags=["Administration"])
    api_router.include_router(data_import_router, prefix="/data", tags=["Data Import"])

    logger.info("✅ All endpoints mounted successfully")
else:
    logger.error("❌ Failed to mount endpoints - API may not be fully functional")