from pydantic import BaseModel, UUID4, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime, date
from decimal import Decimal


class VariantBase(BaseModel):
    variant_sku: str = Field(..., max_length=100)
    processor: Optional[str] = Field(None, max_length=255)
    processor_family: Optional[str] = Field(None, max_length=100)
    processor_speed: Optional[str] = Field(None, max_length=50)
    memory: Optional[str] = Field(None, max_length=100)
    memory_size: Optional[int] = Field(None, ge=0)
    memory_type: Optional[str] = Field(None, max_length=50)
    storage: Optional[str] = Field(None, max_length=100)
    storage_size: Optional[int] = Field(None, ge=0)
    storage_type: Optional[str] = Field(None, max_length=50)
    display: Optional[str] = Field(None, max_length=100)
    display_size: Optional[Decimal] = Field(None, ge=0)
    display_resolution: Optional[str] = Field(None, max_length=50)
    graphics: Optional[str] = Field(None, max_length=255)
    additional_features: Dict = Field(default_factory=dict)
    price: Optional[Decimal] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=50)


class VariantCreate(VariantBase):
    product_id: UUID4


class VariantResponse(VariantBase):
    id: UUID4
    product_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class VariantWithProduct(VariantResponse):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    product_name: str
    brand: str
    model_family: str


class PriceHistoryPoint(BaseModel):
    price: Decimal
    captured_date: date

    class Config:
        from_attributes = True


class VariantWithPriceHistory(VariantResponse):
    price_history: List[PriceHistoryPoint] = []

    class Config:
        from_attributes = True


class VariantComparison(BaseModel):
    variants: List[VariantResponse]
    comparison_matrix: Dict[str, List[str]]
    differences: List[str]

    class Config:
        from_attributes = True