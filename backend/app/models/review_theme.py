from sqlalchemy import Column, String, Text, DECIMAL, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ReviewTheme(Base):
    __tablename__ = "review_themes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    theme = Column(String(100), nullable=False, index=True)
    aspect = Column(String(100))  # battery, performance, build_quality, keyboard, etc.
    sentiment = Column(String(20))  # positive, negative, neutral
    confidence = Column(DECIMAL(3, 2))
    mention_count = Column(Integer, default=1)
    example_quotes = Column(JSON, default=list)  # Sample review snippets
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="review_themes")

    def __repr__(self):
        return f"<ReviewTheme(id={self.id}, theme={self.theme}, sentiment={self.sentiment})>"


class ReviewAnalytics(Base):
    __tablename__ = "review_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    period = Column(String(20))  # daily, weekly, monthly
    period_date = Column(TIMESTAMP, nullable=False)
    total_reviews = Column(Integer, default=0)
    average_rating = Column(DECIMAL(3, 2))
    rating_distribution = Column(JSON)  # {1: count, 2: count, ...}
    sentiment_distribution = Column(JSON)  # {positive: %, negative: %, neutral: %}
    top_pros = Column(JSON, default=list)
    top_cons = Column(JSON, default=list)
    recommended_for = Column(JSON, default=list)
    not_recommended_for = Column(JSON, default=list)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="review_analytics")

    def __repr__(self):
        return f"<ReviewAnalytics(id={self.id}, product_id={self.product_id}, period={self.period})>"