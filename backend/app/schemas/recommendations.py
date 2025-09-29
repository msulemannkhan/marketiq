from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from decimal import Decimal


class RecommendationConstraints(BaseModel):
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    must_have_features: List[str] = []
    nice_to_have_features: List[str] = []
    brands: Optional[List[str]] = None
    min_rating: Optional[Decimal] = Field(None, ge=1, le=5)
    use_cases: List[str] = []  # business, gaming, programming, etc.
    processor_preference: Optional[str] = None  # Intel, AMD
    min_memory_gb: Optional[int] = None
    min_storage_gb: Optional[int] = None
    display_size_preference: Optional[str] = None  # 14", 15.6"


class RecommendationRequest(BaseModel):
    constraints: RecommendationConstraints
    max_results: int = Field(default=5, ge=1, le=20)
    include_rationale: bool = True
    include_alternatives: bool = False
    user_context: Optional[str] = None  # Additional context from user


class ProductRecommendation(BaseModel):
    product_id: UUID4
    variant_id: Optional[UUID4] = None
    product_name: str
    brand: str
    price: Decimal
    match_score: int = Field(ge=0, le=100)  # How well it matches requirements
    rationale: Dict[str, Any] = {}  # Why this is recommended
    pros: List[str] = []
    cons: List[str] = []
    best_for: List[str] = []
    citations: List[Dict[str, str]] = []  # Source citations


class RecommendationResponse(BaseModel):
    request_id: UUID4
    timestamp: datetime
    constraints_summary: str
    recommendations: List[ProductRecommendation]
    alternatives: Optional[List[ProductRecommendation]] = None
    trade_offs: List[str] = []  # What compromises were made
    insights: List[str] = []  # Market insights
    no_match_reason: Optional[str] = None  # If no products match

    class Config:
        from_attributes = True


class ComparisonRecommendation(BaseModel):
    product_ids: List[UUID4]
    comparison_aspects: List[str]
    winner: Optional[UUID4] = None
    winner_rationale: Optional[str] = None
    detailed_comparison: Dict[str, Dict[str, Any]] = {}
    use_case_winners: Dict[str, UUID4] = {}  # Best for different use cases
    verdict: str

    class Config:
        from_attributes = True


class SmartRecommendation(BaseModel):
    recommendation_type: str  # budget_best, performance_best, value_best, etc.
    title: str
    description: str
    products: List[ProductRecommendation]
    target_audience: List[str]
    key_benefits: List[str]
    valid_until: Optional[datetime] = None

    class Config:
        from_attributes = True