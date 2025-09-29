"""
Review Analytics Endpoints
Provides review intelligence and analytics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.review_intelligence import ReviewIntelligenceService
from app.services.analytics_service import AnalyticsService
from app.schemas.review_analytics import ReviewInsights, ReviewTrendAnalysis

router = APIRouter()


@router.get("/products/{product_id}/reviews/analysis", response_model=ReviewInsights)
async def get_product_review_analysis(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive review analysis for a product"""
    try:
        analysis = ReviewIntelligenceService.analyze_product_reviews(product_id, db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/products/{product_id}/reviews/trends", response_model=ReviewTrendAnalysis)
async def get_product_review_trends(
    product_id: uuid.UUID,
    period: str = Query("monthly", regex="^(weekly|monthly|quarterly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get review trends over time for a product"""
    try:
        trends = ReviewIntelligenceService.get_review_trends(product_id, period, db)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.get("/products/{product_id}/reviews/themes")
async def get_product_review_themes(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top review themes and sentiment for a product"""
    try:
        analysis = ReviewIntelligenceService.analyze_product_reviews(product_id, db)
        return {
            "product_id": product_id,
            "themes": analysis.themes,
            "sentiment_summary": analysis.sentiment_summary,
            "top_pros": analysis.top_pros,
            "top_cons": analysis.top_cons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theme analysis failed: {str(e)}")


@router.get("/analytics/reviews/summary")
async def get_reviews_summary(
    brand: Optional[str] = Query(None),
    period: str = Query("monthly", regex="^(weekly|monthly|quarterly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cross-product review analytics summary"""
    try:
        service = AnalyticsService(db)
        summary = service.get_review_analytics_summary(brand, period)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")