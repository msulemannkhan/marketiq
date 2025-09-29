from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    context: Optional[Dict] = Field(default_factory=dict)
    start_new: bool = False


class Citation(BaseModel):
    product_name: str
    sku: str
    url: Optional[str] = None
    relevance_score: Optional[float] = Field(None, ge=0, le=1)


class Recommendation(BaseModel):
    variant_id: str
    product_name: str
    configuration: Dict
    price: Optional[float]
    score: float
    rationale: str


class ChatResponse(BaseModel):
    response: str
    citations: List[Citation] = Field(default_factory=list)
    recommendations: Optional[List[Recommendation]] = None
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0


class ChatHistory(BaseModel):
    session_id: str
    messages: List[Dict] = Field(default_factory=list)  # [{user, assistant, timestamp}]

    class Config:
        from_attributes = True