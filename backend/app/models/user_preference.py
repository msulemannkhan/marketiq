from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    preferences = Column(JSON, default=dict)  # {budget_range: {}, brand_preference: [], use_cases: []}
    search_history = Column(JSON, default=list)  # Recent searches
    viewed_products = Column(ARRAY(UUID(as_uuid=True)), default=list)
    saved_searches = Column(JSON, default=list)
    comparison_history = Column(JSON, default=list)
    notification_settings = Column(JSON, default=dict)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    query = Column(String(500))
    filters = Column(JSON)
    results_count = Column(Integer)
    clicked_results = Column(ARRAY(UUID(as_uuid=True)), default=list)
    search_type = Column(String(50))  # standard, semantic, advanced
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="search_history")

    def __repr__(self):
        return f"<SearchHistory(id={self.id}, user_id={self.user_id}, query={self.query})>"


class UserRecommendation(Base):
    __tablename__ = "user_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"))
    recommendation_type = Column(String(50))  # personalized, similar, trending
    score = Column(Integer)  # Recommendation confidence score
    rationale = Column(JSON)  # Explanation for recommendation
    shown_count = Column(Integer, default=0)
    clicked = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    product = relationship("Product")
    variant = relationship("Variant")

    def __repr__(self):
        return f"<UserRecommendation(id={self.id}, user_id={self.user_id}, product_id={self.product_id})>"