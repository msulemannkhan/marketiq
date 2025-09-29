"""
Dashboard and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import Product, Variant, User
import random

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview with key metrics"""

    # Get basic counts
    total_products = db.query(Product).count()
    total_variants = db.query(Variant).count()
    total_brands = db.query(Product.brand).distinct().count()

    # Get price statistics
    avg_price = db.query(func.avg(Product.base_price)).scalar() or 0

    # Mock metrics (replace with actual calculations)
    metrics = {
        "total_products": total_products,
        "total_variants": total_variants,
        "total_brands": total_brands,
        "average_price": round(float(avg_price), 2),
        "total_reviews": random.randint(1000, 5000),
        "average_rating": round(random.uniform(4.0, 4.5), 2),
        "products_in_stock": int(total_products * 0.85),
        "products_on_sale": int(total_products * 0.15)
    }

    # Mock trend data
    trends = {
        "products_growth": "+12.5%",
        "reviews_growth": "+25.3%",
        "sales_growth": "+8.7%"
    }

    return {
        "metrics": metrics,
        "trends": trends,
        "last_updated": datetime.now().isoformat()
    }


@router.get("/sales-analytics")
async def get_sales_analytics(
    period: str = Query("7d", regex="^(1d|7d|30d|90d|1y)$"),
    db: Session = Depends(get_db)
):
    """Get sales analytics for dashboard"""

    # Mock sales data (replace with actual data)
    if period == "1d":
        data_points = 24  # Hourly
    elif period == "7d":
        data_points = 7   # Daily
    elif period == "30d":
        data_points = 30  # Daily
    elif period == "90d":
        data_points = 13  # Weekly
    else:
        data_points = 12  # Monthly

    sales_data = []
    for i in range(data_points):
        sales_data.append({
            "date": (datetime.now() - timedelta(days=data_points-i)).strftime("%Y-%m-%d"),
            "sales": random.randint(50, 200),
            "revenue": random.randint(50000, 200000),
            "units": random.randint(100, 500)
        })

    return {
        "period": period,
        "sales_data": sales_data,
        "summary": {
            "total_sales": sum(d["sales"] for d in sales_data),
            "total_revenue": sum(d["revenue"] for d in sales_data),
            "total_units": sum(d["units"] for d in sales_data),
            "average_order_value": round(sum(d["revenue"] for d in sales_data) / sum(d["sales"] for d in sales_data), 2)
        }
    }


@router.get("/product-performance")
async def get_product_performance(
    limit: int = Query(10, ge=1, le=50),
    metric: str = Query("revenue", regex="^(revenue|units|rating|reviews)$"),
    db: Session = Depends(get_db)
):
    """Get top performing products"""

    products = db.query(Product).limit(limit).all()

    performance_data = []
    for product in products:
        # Mock performance metrics (replace with actual data)
        performance_data.append({
            "product_id": product.id,
            "product_name": product.product_name,
            "brand": product.brand,
            "revenue": random.randint(10000, 100000),
            "units_sold": random.randint(10, 200),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "review_count": random.randint(50, 500),
            "conversion_rate": f"{random.uniform(1, 5):.1f}%"
        })

    # Sort by requested metric
    if metric == "revenue":
        performance_data.sort(key=lambda x: x["revenue"], reverse=True)
    elif metric == "units":
        performance_data.sort(key=lambda x: x["units_sold"], reverse=True)
    elif metric == "rating":
        performance_data.sort(key=lambda x: x["rating"], reverse=True)
    elif metric == "reviews":
        performance_data.sort(key=lambda x: x["review_count"], reverse=True)

    return {
        "metric": metric,
        "top_products": performance_data[:limit]
    }


@router.get("/customer-insights")
async def get_customer_insights(db: Session = Depends(get_db)):
    """Get customer behavior insights"""

    # Mock customer insights (replace with actual data)
    insights = {
        "total_customers": random.randint(5000, 10000),
        "new_customers_this_month": random.randint(500, 1500),
        "returning_customer_rate": f"{random.uniform(30, 50):.1f}%",
        "average_session_duration": f"{random.randint(5, 15)} minutes",
        "popular_categories": [
            {"category": "Business Laptops", "percentage": 35},
            {"category": "Gaming Laptops", "percentage": 28},
            {"category": "Ultrabooks", "percentage": 22},
            {"category": "Budget Laptops", "percentage": 15}
        ],
        "customer_segments": [
            {"segment": "Business Professional", "count": 3500},
            {"segment": "Student", "count": 2800},
            {"segment": "Gamer", "count": 2200},
            {"segment": "Creative Professional", "count": 1500}
        ]
    }

    return insights


@router.get("/inventory-status")
async def get_inventory_status(db: Session = Depends(get_db)):
    """Get inventory status overview"""

    total_products = db.query(Product).count()

    # Mock inventory data (replace with actual data)
    inventory = {
        "total_products": total_products,
        "in_stock": int(total_products * 0.85),
        "low_stock": int(total_products * 0.10),
        "out_of_stock": int(total_products * 0.05),
        "stock_value": random.randint(1000000, 5000000),
        "low_stock_alerts": [
            {
                "product_id": "prod_001",
                "product_name": "HP Elite Laptop",
                "current_stock": 5,
                "reorder_point": 10
            },
            {
                "product_id": "prod_002",
                "product_name": "Lenovo ThinkPad",
                "current_stock": 3,
                "reorder_point": 15
            }
        ]
    }

    return inventory


@router.get("/review-analytics")
async def get_review_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d)$"),
    db: Session = Depends(get_db)
):
    """Get review analytics for dashboard"""

    # Mock review analytics (replace with actual data)
    analytics = {
        "period": period,
        "total_reviews": random.randint(500, 2000),
        "average_rating": round(random.uniform(4.0, 4.5), 2),
        "rating_distribution": {
            "5_star": 45,
            "4_star": 30,
            "3_star": 15,
            "2_star": 7,
            "1_star": 3
        },
        "sentiment_analysis": {
            "positive": 75,
            "neutral": 18,
            "negative": 7
        },
        "top_keywords": [
            {"keyword": "great performance", "count": 156},
            {"keyword": "good value", "count": 142},
            {"keyword": "fast shipping", "count": 98},
            {"keyword": "excellent build", "count": 87},
            {"keyword": "battery life", "count": 76}
        ],
        "review_trends": []
    }

    # Generate trend data based on period
    if period == "7d":
        days = 7
    elif period == "30d":
        days = 30
    else:
        days = 90

    for i in range(min(days, 30)):  # Limit to 30 data points
        analytics["review_trends"].append({
            "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
            "count": random.randint(10, 50),
            "average_rating": round(random.uniform(4.0, 4.5), 2)
        })

    return analytics