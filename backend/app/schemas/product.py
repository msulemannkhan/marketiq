from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    brand: str = Field(..., max_length=50)
    model_family: str = Field(..., max_length=100)
    base_sku: str = Field(..., max_length=100)
    product_name: str = Field(..., max_length=255)
    product_url: Optional[str] = None
    pdf_spec_url: Optional[str] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    badges: List[str] = Field(default_factory=list)
    offers: List[str] = Field(default_factory=list)


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithVariants(ProductResponse):
    variants: List["VariantResponse"] = []

    class Config:
        from_attributes = True


class ProductSummary(BaseModel):
    id: UUID4
    brand: str
    model_family: str
    product_name: str
    base_price: Optional[Decimal]
    status: Optional[str]
    variant_count: int = 0

    class Config:
        from_attributes = True


# Import here to avoid circular imports
from .variant import VariantResponse
ProductWithVariants.model_rebuild()