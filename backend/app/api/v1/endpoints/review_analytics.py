"""
Review analytics endpoints for insights and trends
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.review_analytics import (
    ReviewInsights, ReviewTrendAnalysis, ReviewThemeResponse,
    ReviewAnalyticsResponse
)
from app.services.review_analytics import ReviewAnalyticsService

router = APIRouter()


@router.get("/{product_id}/reviews/insights", response_model=ReviewInsights)
async def get_review_insights(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive review insights for a product"""
    service = ReviewAnalyticsService(db)
    insights = service.get_review_insights(product_id)

    if not insights:
        raise HTTPException(status_code=404, detail="Product not found")

    return insights


@router.get("/{product_id}/reviews/trends", response_model=ReviewTrendAnalysis)
async def get_review_trends(
    product_id: str,
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    days_back: int = Query(90, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze review trends over time"""
    service = ReviewAnalyticsService(db)
    trends = service.analyze_review_trends(product_id, period, days_back)
    return trends


@router.get("/{product_id}/reviews/themes", response_model=List[ReviewThemeResponse])
async def get_review_themes(
    product_id: str,
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review themes for a product"""
    from app.crud.enhanced_crud import ReviewThemeCRUD

    themes = ReviewThemeCRUD.get_by_product(db, product_id, sentiment, limit)
    return [ReviewThemeResponse.from_orm(theme) for theme in themes]


@router.post("/{product_id}/reviews/analyze")
async def trigger_review_analysis(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger review analysis for a product"""
    service = ReviewAnalyticsService(db)

    # Extract themes
    themes = service.extract_review_themes(product_id)

    # Update analytics
    analytics = service.update_review_analytics(product_id)

    if not analytics:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "message": "Review analysis completed",
        "themes_extracted": len(themes),
        "analytics_updated": True
    }


@router.get("/reviews/analytics", response_model=List[ReviewAnalyticsResponse])
async def get_all_review_analytics(
    limit: int = Query(20, ge=1, le=100),
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get review analytics across all products"""
    from app.crud.enhanced_crud import ReviewAnalyticsCRUD
    from app.models import ReviewAnalytics

    analytics = db.query(ReviewAnalytics).filter(
        ReviewAnalytics.period == period
    ).order_by(ReviewAnalytics.created_at.desc()).limit(limit).all()

    return [ReviewAnalyticsResponse.from_orm(a) for a in analytics]


@router.post("/compare/reviews")
async def compare_review_analytics(
    product_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare review analytics across multiple products"""
    if len(product_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 products required for comparison"
        )

    if len(product_ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 products allowed for comparison"
        )

    service = ReviewAnalyticsService(db)
    comparison = service.get_comparative_review_analysis(product_ids)

    return {
        "comparison": comparison,
        "products_compared": len(product_ids),
        "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }


@router.get("/reviews/top-themes")
async def get_top_themes_across_products(
    limit: int = Query(20, ge=1, le=100),
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get top themes across all products"""
    from app.crud.enhanced_crud import ReviewThemeCRUD

    themes = ReviewThemeCRUD.get_top_themes(db, limit)

    if sentiment:
        themes = [t for t in themes if t.sentiment == sentiment]

    # Group by theme name and aggregate mentions
    theme_aggregates = {}
    for theme in themes:
        theme_name = theme.theme
        if theme_name not in theme_aggregates:
            theme_aggregates[theme_name] = {
                "theme": theme_name,
                "total_mentions": 0,
                "products": set(),
                "sentiments": {}
            }

        theme_aggregates[theme_name]["total_mentions"] += theme.mention_count
        theme_aggregates[theme_name]["products"].add(str(theme.product_id))

        sentiment = theme.sentiment or "neutral"
        theme_aggregates[theme_name]["sentiments"][sentiment] = \
            theme_aggregates[theme_name]["sentiments"].get(sentiment, 0) + theme.mention_count

    # Convert to list and sort by mentions
    result = []
    for theme_data in theme_aggregates.values():
        theme_data["products"] = list(theme_data["products"])
        theme_data["product_count"] = len(theme_data["products"])
        result.append(theme_data)

    result.sort(key=lambda x: x["total_mentions"], reverse=True)

    return {
        "top_themes": result[:limit],
        "total_themes": len(result)
    }