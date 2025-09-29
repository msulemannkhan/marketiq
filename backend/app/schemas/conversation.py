"""
Conversation Schemas
Pydantic schemas for conversation memory and context management
"""
from pydantic import BaseModel, UUID4, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConversationSessionBase(BaseModel):
    user_id: Optional[UUID4] = None
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationSessionCreate(ConversationSessionBase):
    pass


class ConversationSessionResponse(ConversationSessionBase):
    id: UUID4
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationMessageBase(BaseModel):
    message_type: str = Field(..., description="Type of message: user, assistant, system")
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)  # Fixed: Changed from List[str] to List[Dict]


class ConversationMessageCreate(ConversationMessageBase):
    session_id: UUID4


class ConversationMessageResponse(ConversationMessageBase):
    id: UUID4
    session_id: UUID4
    response_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationContextBase(BaseModel):
    context_type: str = Field(..., description="Type of context: user_preferences, search_history, etc.")
    context_data: Dict[str, Any] = Field(..., description="Context data as JSON")


class ConversationContextCreate(ConversationContextBase):
    session_id: UUID4


class ConversationContextResponse(ConversationContextBase):
    id: UUID4
    session_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationFeedbackBase(BaseModel):
    feedback_type: str = Field(..., description="Type of feedback: helpful, not_helpful, inaccurate, excellent")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")
    comment: Optional[str] = Field(None, max_length=1000)


class ConversationFeedbackCreate(ConversationFeedbackBase):
    session_id: UUID4
    message_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None


class ConversationFeedbackResponse(ConversationFeedbackBase):
    id: UUID4
    session_id: UUID4
    message_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    session_id: UUID4
    status: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: str = ""
    topics: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationInsights(BaseModel):
    preferences: Dict[str, Any] = Field(default_factory=dict)
    conversation_length: int = 0
    user_engagement: int = 0
    tool_usage: Dict[str, Any] = Field(default_factory=dict)
    topics_discussed: List[str] = Field(default_factory=list)
    decision_stage: str = "initial"
    next_actions: List[str] = Field(default_factory=list)


class ConversationHistoryResponse(BaseModel):
    session: ConversationSessionResponse
    messages: List[ConversationMessageResponse]
    context: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)


class ConversationMemoryUpdate(BaseModel):
    context_type: str
    context_data: Dict[str, Any]
    merge_with_existing: bool = True


class ConversationAnalyticsCreate(BaseModel):
    session_id: UUID4
    metric_type: str
    metric_value: Dict[str, Any]


class ConversationAnalyticsResponse(BaseModel):
    id: UUID4
    session_id: UUID4
    metric_type: str
    metric_value: Dict[str, Any]
    recorded_at: datetime

    class Config:
        from_attributes = True


class AgenticChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[UUID4] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    enable_memory: bool = True
    enable_tool_chaining: bool = True
    max_tool_calls: int = Field(default=5, ge=1, le=20)
    user_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgenticChatResponse(BaseModel):
    response: str
    session_id: UUID4
    tool_calls_made: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)  # Fixed: Changed from List[str] to List[Dict]
    recommendations: Optional[List[Dict[str, Any]]] = None
    conversation_insights: Optional[ConversationInsights] = None
    next_suggested_questions: List[str] = Field(default_factory=list)
    response_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None


class ConversationSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    session_ids: Optional[List[UUID4]] = None
    message_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=200)


class ConversationSearchResponse(BaseModel):
    total_found: int
    messages: List[ConversationMessageResponse]
    sessions: List[ConversationSessionResponse]


class ConversationExportRequest(BaseModel):
    session_ids: Optional[List[UUID4]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_context: bool = True
    include_analytics: bool = False
    format: str = Field(default="json", pattern="^(json|csv|xml)$")


class ConversationExportResponse(BaseModel):
    export_id: UUID4
    download_url: str
    format: str
    record_count: int
    expires_at: datetime