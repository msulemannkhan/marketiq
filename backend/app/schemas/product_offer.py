from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductOfferBase(BaseModel):
    badge: Optional[str] = Field(None, max_length=100)
    offer_text: str = Field(..., min_length=5, max_length=500)
    offer_type: Optional[str] = Field(None, max_length=50)  # DISCOUNT, FREE_SHIPPING, BUNDLE
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    promo_code: Optional[str] = Field(None, max_length=50)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    active: bool = True


class ProductOfferCreate(ProductOfferBase):
    product_id: UUID4
    variant_id: Optional[UUID4] = None


class ProductOfferUpdate(BaseModel):
    badge: Optional[str] = None
    offer_text: Optional[str] = None
    offer_type: Optional[str] = None
    discount_amount: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    promo_code: Optional[str] = None
    valid_until: Optional[datetime] = None
    active: Optional[bool] = None


class ProductOfferResponse(ProductOfferBase):
    id: UUID4
    product_id: UUID4
    variant_id: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OfferSummary(BaseModel):
    total_offers: int = 0
    active_offers: int = 0
    best_discount: Optional[ProductOfferResponse] = None
    offers_by_type: dict[str, int] = {}

    class Config:
        from_attributes = True