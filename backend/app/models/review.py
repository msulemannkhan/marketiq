from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, JSON, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    rating = Column(DECIMAL(2, 1), nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    reviewer_name = Column(String, nullable=True)
    review_date = Column(DateTime, nullable=False, default=func.now())
    verified_purchase = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    sentiment = Column(JSON, nullable=True)  # Pre-analyzed sentiment
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review(product_id={self.product_id}, rating={self.rating}, reviewer={self.reviewer_name})>"


class ReviewSummary(Base):
    __tablename__ = "review_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    # Review metrics
    total_reviews = Column(Integer, default=0)
    average_rating = Column(DECIMAL(3, 2))
    rating_distribution = Column(JSON, default=dict)  # e.g., {"5": 20, "4": 15, ...}

    # Extracted insights
    top_pros = Column(ARRAY(Text), default=list)
    top_cons = Column(ARRAY(Text), default=list)

    # Sample reviews for display
    sample_reviews = Column(JSON, default=list)  # Array of review objects

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="review_summary")

    def __repr__(self):
        return f"<ReviewSummary(product_id={self.product_id}, total={self.total_reviews}, avg={self.average_rating})>"