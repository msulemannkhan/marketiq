"""
Analytics Dashboard Endpoints
Provides comprehensive analytics and market insights
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.product import Product
from app.models.variant import Variant
from app.models.review import ReviewSummary
from app.models.price import PriceHistory
from app.models.product_offer import ProductOffer
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/analytics/dashboard/overview")
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get high-level analytics overview for dashboard"""
    try:
        service = AnalyticsService(db)
        overview = service.get_dashboard_overview()
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch overview: {str(e)}")


@router.get("/analytics/products/stats")
async def get_product_statistics(
    brand: Optional[str] = Query(None),
    time_period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive product statistics"""
    try:
        service = AnalyticsService(db)
        stats = service.get_product_statistics(brand, time_period)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product stats: {str(e)}")


@router.get("/analytics/price-trends")
async def get_price_trends(
    product_id: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    days: int = Query(30, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price trend analysis"""
    try:
        service = AnalyticsService(db)
        trends = service.get_price_trends(product_id, brand, days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price trends: {str(e)}")


@router.get("/analytics/market/insights")
async def get_market_insights(
    segment: Optional[str] = Query(None, regex="^(budget|premium|business|gaming)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market insights and trends"""
    try:
        service = AnalyticsService(db)
        insights = service.get_market_insights(segment)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market insights: {str(e)}")


@router.get("/analytics/reviews/summary")
async def get_reviews_analytics_summary(
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
        raise HTTPException(status_code=500, detail=f"Failed to fetch review summary: {str(e)}")


@router.get("/analytics/performance/metrics")
async def get_performance_metrics(
    metric_type: str = Query("all", regex="^(all|sales|ratings|engagement|technical)$"),
    comparison_period: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance metrics and KPIs"""
    try:
        service = AnalyticsService(db)
        metrics = service.get_performance_metrics(metric_type, comparison_period)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")


@router.get("/analytics/brands/comparison")
async def get_brand_comparison(
    brands: List[str] = Query(["HP", "Lenovo"]),
    metrics: List[str] = Query(["rating", "price", "market_share"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed brand comparison analytics"""
    try:
        service = AnalyticsService(db)
        comparison = service.get_brand_comparison(brands, metrics)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch brand comparison: {str(e)}")


@router.get("/analytics/trends/forecasting")
async def get_trend_forecasting(
    forecast_type: str = Query("price", regex="^(price|demand|rating|market)$"),
    forecast_period: int = Query(30, le=180),
    confidence_level: float = Query(0.95, ge=0.8, le=0.99),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get predictive analytics and trend forecasting"""
    try:
        service = AnalyticsService(db)
        forecast = service.get_trend_forecasting(forecast_type, forecast_period, confidence_level)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")


@router.get("/analytics/competitive/intelligence")
async def get_competitive_intelligence(
    focus_area: str = Query("pricing", regex="^(pricing|features|market_position|customer_satisfaction)$"),
    competitor_analysis: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get competitive intelligence insights"""
    try:
        service = AnalyticsService(db)
        intelligence = service.get_competitive_intelligence(focus_area, competitor_analysis)
        return intelligence
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch competitive intelligence: {str(e)}")


@router.get("/analytics/segments/analysis")
async def get_segment_analysis(
    segment_by: str = Query("price_range", regex="^(price_range|use_case|features|brand)$"),
    include_growth: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market segment analysis"""
    try:
        service = AnalyticsService(db)
        analysis = service.get_segment_analysis(segment_by, include_growth)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch segment analysis: {str(e)}")


@router.get("/analytics/recommendations/performance")
async def get_recommendation_performance(
    time_period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    recommendation_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recommendation system performance analytics"""
    try:
        service = AnalyticsService(db)
        performance = service.get_recommendation_performance(time_period, recommendation_type)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recommendation performance: {str(e)}")


@router.get("/analytics/export/data")
async def export_analytics_data(
    data_type: str = Query("summary", regex="^(summary|detailed|raw|dashboard)$"),
    format_type: str = Query("json", regex="^(json|csv|excel)$"),
    include_metadata: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    try:
        service = AnalyticsService(db)
        export_data = service.export_analytics_data(data_type, format_type, include_metadata)

        if format_type == "json":
            return export_data
        else:
            # For CSV/Excel, would typically return a file download response
            return {
                "export_id": export_data.get("export_id"),
                "download_url": f"/api/v1/analytics/export/{export_data.get('export_id')}/download",
                "format": format_type,
                "expires_at": export_data.get("expires_at")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.get("/analytics/alerts/configuration")
async def get_analytics_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get configured analytics alerts and thresholds"""
    try:
        # Mock implementation - would integrate with alert system
        alerts = {
            "price_drop_alerts": {
                "enabled": True,
                "threshold_percentage": 10,
                "notification_methods": ["email", "dashboard"]
            },
            "stock_alerts": {
                "enabled": True,
                "low_stock_threshold": 5,
                "out_of_stock_enabled": True
            },
            "rating_alerts": {
                "enabled": True,
                "threshold_drop": 0.5,
                "review_count_minimum": 10
            },
            "market_trend_alerts": {
                "enabled": True,
                "significant_change_threshold": 15
            }
        }
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")


@router.post("/analytics/alerts/configure")
async def configure_analytics_alerts(
    alert_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Configure analytics alerts and thresholds"""
    try:
        # Mock implementation - would save to database
        return {
            "success": True,
            "message": "Alert configuration updated successfully",
            "updated_alerts": list(alert_config.keys()),
            "effective_date": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure alerts: {str(e)}")