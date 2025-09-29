"""
Conversation Models
Database models for conversation memory and context management
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(20), default="active", index=True)  # active, closed, expired
    message_count = Column(Integer, default=0)
    session_metadata = Column(JSON, default=dict)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversation_sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConversationSession(id={self.id}, user_id={self.user_id}, status={self.status})>"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    message_type = Column(String(20), nullable=False, index=True)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict)
    tool_calls = Column(JSON, default=list)  # Store tool calls made by assistant
    citations = Column(JSON, default=list)  # Store citations/sources
    response_time_ms = Column(Integer, nullable=True)  # Response time for assistant messages
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    session = relationship("ConversationSession", back_populates="messages")

    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, type={self.message_type}, session={self.session_id})>"


class ConversationContext(Base):
    __tablename__ = "conversation_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    context_type = Column(String(50), nullable=False, index=True)  # user_preferences, search_history, etc.
    context_data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    session = relationship("ConversationSession", back_populates="contexts")

    def __repr__(self):
        return f"<ConversationContext(id={self.id}, type={self.context_type}, session={self.session_id})>"


class ConversationFeedback(Base):
    __tablename__ = "conversation_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("conversation_messages.id"), nullable=True, index=True)
    feedback_type = Column(String(20), nullable=False)  # helpful, not_helpful, inaccurate, excellent
    rating = Column(Integer, nullable=True)  # 1-5 rating
    comment = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    session = relationship("ConversationSession")
    message = relationship("ConversationMessage")
    user = relationship("User")

    def __repr__(self):
        return f"<ConversationFeedback(id={self.id}, type={self.feedback_type}, session={self.session_id})>"


class ConversationAnalytics(Base):
    __tablename__ = "conversation_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False, index=True)  # response_time, tool_usage, satisfaction
    metric_value = Column(JSON, nullable=False)  # Store metric data as JSON
    recorded_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    session = relationship("ConversationSession")

    def __repr__(self):
        return f"<ConversationAnalytics(id={self.id}, metric={self.metric_type}, session={self.session_id})>"