from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal
from .variant import VariantWithProduct


class SearchFilters(BaseModel):
    brand: Optional[str] = Field(None, max_length=50)
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    processor_family: Optional[str] = Field(None, max_length=100)
    min_memory: Optional[int] = Field(None, ge=0)
    storage_type: Optional[str] = Field(None, max_length=50)
    min_storage_size: Optional[int] = Field(None, ge=0)


class SearchRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=500)
    filters: Optional[SearchFilters] = None
    sort_by: Optional[str] = Field("price", pattern="^(price|rating|name|performance)$")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")
    limit: Optional[int] = Field(10, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)


class SearchResult(BaseModel):
    variant: VariantWithProduct
    relevance_score: Optional[float] = Field(None, ge=0, le=1)
    match_reasons: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    filters_applied: Dict
    query: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)


class FilterOptions(BaseModel):
    brands: List[str]
    processor_families: List[str]
    memory_sizes: List[int]
    storage_types: List[str]
    price_range: Dict[str, Decimal]
    display_sizes: List[Decimal]


class AutoCompleteResponse(BaseModel):
    suggestions: List[str]
    categories: Dict[str, List[str]]  # e.g., {"brands": ["HP", "Lenovo"], "models": [...]}


class TrendingSearches(BaseModel):
    queries: List[str]
    filters: List[Dict]
    timestamp: str