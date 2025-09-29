from pydantic import BaseModel, UUID4, Field
from typing import Optional
from datetime import datetime


class ProductQABase(BaseModel):
    question: str = Field(..., min_length=10, max_length=1000)
    answer: str = Field(..., min_length=10, max_length=5000)
    author: Optional[str] = Field(None, max_length=100)
    verified: bool = False


class ProductQACreate(ProductQABase):
    product_id: UUID4


class ProductQAUpdate(BaseModel):
    answer: Optional[str] = Field(None, min_length=10, max_length=5000)
    verified: Optional[bool] = None
    votes: Optional[int] = None
    helpful_count: Optional[int] = None


class ProductQAResponse(ProductQABase):
    id: UUID4
    product_id: UUID4
    votes: int = 0
    helpful_count: int = 0
    asked_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductQASummary(BaseModel):
    total_questions: int = 0
    verified_questions: int = 0
    most_helpful: list[ProductQAResponse] = []
    recent_questions: list[ProductQAResponse] = []

    class Config:
        from_attributes = True


class TrendingQuestionResponse(BaseModel):
    id: UUID4
    product_id: UUID4
    question_text: str
    category: Optional[str] = None
    helpful_count: int = 0
    answer_count: int = 0

    class Config:
        from_attributes = True