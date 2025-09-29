from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class UserPreferenceBase(BaseModel):
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, bool] = Field(default_factory=dict)


class UserPreferenceCreate(UserPreferenceBase):
    user_id: UUID4


class UserPreferenceUpdate(BaseModel):
    preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, bool]] = None
    viewed_products: Optional[List[UUID4]] = None
    saved_searches: Optional[List[Dict]] = None


class UserPreferenceResponse(UserPreferenceBase):
    id: UUID4
    user_id: UUID4
    search_history: List[Dict] = []
    viewed_products: List[UUID4] = []
    saved_searches: List[Dict] = []
    comparison_history: List[Dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SearchHistoryBase(BaseModel):
    query: Optional[str] = Field(None, max_length=500)
    filters: Optional[Dict[str, Any]] = None
    search_type: Optional[str] = Field(None, max_length=50)  # standard, semantic, advanced


class SearchHistoryCreate(SearchHistoryBase):
    user_id: UUID4
    results_count: Optional[int] = 0
    clicked_results: Optional[List[UUID4]] = []


class SearchHistoryResponse(SearchHistoryBase):
    id: UUID4
    user_id: UUID4
    results_count: int = 0
    clicked_results: List[UUID4] = []
    created_at: datetime

    class Config:
        from_attributes = True


class UserRecommendationBase(BaseModel):
    recommendation_type: str = Field(..., max_length=50)  # personalized, similar, trending
    score: Optional[int] = Field(None, ge=0, le=100)
    rationale: Optional[Dict[str, Any]] = None


class UserRecommendationCreate(UserRecommendationBase):
    user_id: UUID4
    product_id: UUID4
    variant_id: Optional[UUID4] = None
    expires_at: Optional[datetime] = None


class UserRecommendationResponse(UserRecommendationBase):
    id: UUID4
    user_id: UUID4
    product_id: UUID4
    variant_id: Optional[UUID4] = None
    shown_count: int = 0
    clicked: int = 0
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonalizedRecommendations(BaseModel):
    user_id: UUID4
    recommendations: List[UserRecommendationResponse] = []
    based_on: Dict[str, Any] = {}  # What the recommendations are based on
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True