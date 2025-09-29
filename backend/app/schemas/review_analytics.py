from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal


class ReviewThemeBase(BaseModel):
    theme: str = Field(..., max_length=100)
    aspect: Optional[str] = Field(None, max_length=100)  # battery, performance, build_quality, etc.
    sentiment: Optional[str] = Field(None, max_length=20)  # positive, negative, neutral
    confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    mention_count: int = Field(default=1, ge=0)


class ReviewThemeCreate(ReviewThemeBase):
    product_id: UUID4
    example_quotes: Optional[List[str]] = []


class ReviewThemeResponse(ReviewThemeBase):
    id: UUID4
    product_id: UUID4
    example_quotes: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewAnalyticsBase(BaseModel):
    period: str = Field(..., max_length=20)  # daily, weekly, monthly
    period_date: datetime
    total_reviews: int = 0
    average_rating: Optional[Decimal] = Field(None, ge=1, le=5)
    rating_distribution: Dict[str, int] = {}  # {"1": count, "2": count, ...}
    sentiment_distribution: Dict[str, float] = {}  # {"positive": %, "negative": %, "neutral": %}


class ReviewAnalyticsCreate(ReviewAnalyticsBase):
    product_id: UUID4
    top_pros: List[str] = []
    top_cons: List[str] = []
    recommended_for: List[str] = []
    not_recommended_for: List[str] = []


class ReviewAnalyticsResponse(ReviewAnalyticsBase):
    id: UUID4
    product_id: UUID4
    top_pros: List[str] = []
    top_cons: List[str] = []
    recommended_for: List[str] = []
    not_recommended_for: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewInsights(BaseModel):
    product_id: UUID4
    total_reviews: int = 0
    average_rating: Optional[Decimal] = None
    rating_trend: str = "stable"  # improving, declining, stable
    themes: List[ReviewThemeResponse] = []
    sentiment_summary: Dict[str, float] = {}
    top_pros: List[str] = []
    top_cons: List[str] = []
    recommended_for: List[str] = []
    not_recommended_for: List[str] = []
    key_insights: List[str] = []

    class Config:
        from_attributes = True


class ReviewTrendAnalysis(BaseModel):
    product_id: UUID4
    period: str  # daily, weekly, monthly
    trend_data: List[Dict] = []  # time series data
    rating_trend: str  # improving, declining, stable
    volume_trend: str  # increasing, decreasing, stable
    sentiment_shift: Dict[str, float] = {}  # change in sentiment over time

    class Config:
        from_attributes = True