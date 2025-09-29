"""
Product offers and promotions endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.product_offer import ProductOffer
from app.schemas import (
    ProductOfferCreate, ProductOfferUpdate, ProductOfferResponse, OfferSummary
)
from app.crud.enhanced_crud import ProductOfferCRUD

router = APIRouter()


@router.get("/{product_id}/offers", response_model=List[ProductOfferResponse])
async def get_product_offers(
    product_id: str,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all offers for a specific product"""
    if active_only:
        offers = ProductOfferCRUD.get_active_by_product(db, product_id)
    else:
        offers = db.query(ProductOffer).filter(
            ProductOffer.product_id == product_id
        ).all()
    return offers


@router.get("/variants/{variant_id}/offers", response_model=List[ProductOfferResponse])
async def get_variant_offers(
    variant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get offers specific to a variant"""
    offers = ProductOfferCRUD.get_by_variant(db, variant_id)
    return offers


@router.post("/{product_id}/offers", response_model=ProductOfferResponse)
async def create_product_offer(
    product_id: str,
    offer_data: ProductOfferCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new offer for a product"""
    offer_data.product_id = product_id
    offer = ProductOfferCRUD.create(db, offer_data)
    return offer


@router.put("/offers/{offer_id}", response_model=ProductOfferResponse)
async def update_offer(
    offer_id: str,
    offer_update: ProductOfferUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an offer"""
    offer = ProductOfferCRUD.update(db, offer_id, offer_update)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@router.get("/{product_id}/offers/summary", response_model=OfferSummary)
async def get_offers_summary(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get offers summary for a product"""
    all_offers = db.query(ProductOffer).filter(
        ProductOffer.product_id == product_id
    ).all()

    active_offers = [o for o in all_offers if o.active]

    # Find best discount
    best_discount = None
    best_amount = 0
    for offer in active_offers:
        if offer.discount_amount and offer.discount_amount > best_amount:
            best_amount = offer.discount_amount
            best_discount = offer

    # Count by type
    offers_by_type = {}
    for offer in active_offers:
        offer_type = offer.offer_type or "general"
        offers_by_type[offer_type] = offers_by_type.get(offer_type, 0) + 1

    return OfferSummary(
        total_offers=len(all_offers),
        active_offers=len(active_offers),
        best_discount=best_discount,
        offers_by_type=offers_by_type
    )


@router.get("/offers/active", response_model=List[ProductOfferResponse])
async def get_all_active_offers(
    limit: int = Query(50, le=100),
    offer_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all active offers across products"""
    try:
        from datetime import datetime
        query = db.query(ProductOffer).filter(ProductOffer.active == True)

        # Filter by valid date
        query = query.filter(
            or_(
                ProductOffer.valid_until.is_(None),
                ProductOffer.valid_until > datetime.utcnow()
            )
        )

        # Filter by offer type if specified
        if offer_type:
            query = query.filter(ProductOffer.offer_type == offer_type)

        offers = query.order_by(ProductOffer.discount_amount.desc()).limit(limit).all()
        return offers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch active offers: {str(e)}")


@router.get("/offers/trending", response_model=List[dict])
async def get_trending_offers(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get trending/popular offers"""
    try:
        from datetime import datetime, timedelta
        # Get offers from last 30 days with highest discounts
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        trending_offers = db.query(ProductOffer).filter(
            ProductOffer.active == True,
            ProductOffer.created_at >= cutoff_date,
            ProductOffer.discount_amount.isnot(None)
        ).order_by(ProductOffer.discount_amount.desc()).limit(limit).all()

        return [
            {
                "id": offer.id,
                "product_id": offer.product_id,
                "title": offer.title,
                "description": offer.description,
                "discount_amount": offer.discount_amount,
                "discount_percentage": offer.discount_percentage,
                "offer_type": offer.offer_type,
                "valid_until": offer.valid_until,
                "created_at": offer.created_at
            }
            for offer in trending_offers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending offers: {str(e)}")


@router.get("/offers/best-deals")
async def get_best_deals(
    limit: int = Query(10, le=50),
    min_discount: float = Query(0.0),
    db: Session = Depends(get_db)
):
    """Get best deals based on discount percentage or amount"""
    try:
        from datetime import datetime
        query = db.query(ProductOffer).filter(
            ProductOffer.active == True,
            or_(
                ProductOffer.valid_until.is_(None),
                ProductOffer.valid_until > datetime.utcnow()
            )
        )

        # Filter by minimum discount
        if min_discount > 0:
            query = query.filter(
                or_(
                    ProductOffer.discount_amount >= min_discount,
                    ProductOffer.discount_percentage >= min_discount
                )
            )

        # Order by best discount (prioritize percentage, then amount)
        best_deals = query.order_by(
            ProductOffer.discount_percentage.desc().nullslast(),
            ProductOffer.discount_amount.desc().nullslast()
        ).limit(limit).all()

        return [
            {
                "id": offer.id,
                "product_id": offer.product_id,
                "variant_id": offer.variant_id,
                "title": offer.title,
                "description": offer.description,
                "discount_amount": offer.discount_amount,
                "discount_percentage": offer.discount_percentage,
                "original_price": getattr(offer, 'original_price', None),
                "final_price": getattr(offer, 'final_price', None),
                "savings": offer.discount_amount or (
                    getattr(offer, 'original_price', 0) * (offer.discount_percentage or 0) / 100
                ),
                "offer_type": offer.offer_type,
                "valid_until": offer.valid_until
            }
            for offer in best_deals
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch best deals: {str(e)}")


@router.post("/admin/offers/cleanup")
async def cleanup_expired_offers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin endpoint to cleanup expired offers"""
    # Add admin check here if needed

    count = ProductOfferCRUD.deactivate_expired(db)
    return {"message": f"Deactivated {count} expired offers"}