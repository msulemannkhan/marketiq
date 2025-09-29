"""
Price history tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
from app.core.database import get_db
from app.models import Product, Variant

router = APIRouter()


@router.get("/{product_id}/price-history")
async def get_price_history(
    product_id: str,  # UUID string format
    days: int = Query(30, ge=7, le=365, description="Number of days of history"),
    db: Session = Depends(get_db)
):
    """Get price history for a specific product"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # For now, return mock price history (replace with actual PriceHistory model query)
    base_price = float(product.base_price) if product.base_price else 1000
    history = []

    for i in range(days, 0, -7):  # Weekly data points
        date = datetime.now() - timedelta(days=i)
        # Generate slight price variation
        price_variation = random.uniform(0.95, 1.05)
        price = round(base_price * price_variation, 2)

        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "currency": "USD",
            "was_on_sale": price < base_price * 0.98
        })

    # Current price
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price": float(product.base_price) if product.base_price else base_price,
        "currency": "USD",
        "was_on_sale": False
    })

    return {
        "product_id": product_id,
        "product_name": product.product_name,
        "price_history": history,
        "lowest_price": min(h["price"] for h in history),
        "highest_price": max(h["price"] for h in history),
        "average_price": round(sum(h["price"] for h in history) / len(history), 2),
        "current_price": float(product.base_price) if product.base_price else base_price,
        "days_tracked": days
    }


@router.get("/{product_id}/price-alerts")
async def get_price_alerts(
    product_id: str,
    db: Session = Depends(get_db)
):
    """Get price drop alerts for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    current_price = float(product.base_price) if product.base_price else 0

    # Mock alerts (replace with actual implementation)
    alerts = []
    if current_price > 0:
        alerts.append({
            "type": "price_drop",
            "threshold": current_price * 0.9,
            "message": f"Alert when price drops below ${current_price * 0.9:.2f}",
            "active": True
        })

    return {
        "product_id": product_id,
        "product_name": product.product_name,
        "current_price": current_price,
        "alerts": alerts
    }


@router.post("/{product_id}/price-alerts")
async def create_price_alert(
    product_id: str,
    target_price: float = Query(..., description="Target price for alert"),
    alert_type: str = Query("price_drop", description="Type of alert: price_drop, price_increase"),
    db: Session = Depends(get_db)
):
    """Create a price alert for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # In production, save this to database
    return {
        "message": "Price alert created successfully",
        "product_id": product_id,
        "product_name": product.product_name,
        "alert": {
            "type": alert_type,
            "target_price": target_price,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
    }