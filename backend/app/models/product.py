from sqlalchemy import Column, String, DECIMAL, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand = Column(String(50), nullable=False, index=True)
    model_family = Column(String(100), nullable=False, index=True)
    base_sku = Column(String(100), unique=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    product_url = Column(Text)
    pdf_spec_url = Column(Text)
    base_price = Column(DECIMAL(10, 2))
    original_price = Column(DECIMAL(10, 2))
    status = Column(String(50))
    badges = Column(JSON, default=list)
    offers = Column(ARRAY(Text), default=list)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    variants = relationship("Variant", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    review_summary = relationship("ReviewSummary", back_populates="product", uselist=False)
    qa_items = relationship("ProductQA", back_populates="product", cascade="all, delete-orphan")
    product_offers = relationship("ProductOffer", back_populates="product", cascade="all, delete-orphan")
    review_themes = relationship("ReviewTheme", back_populates="product", cascade="all, delete-orphan")
    review_analytics = relationship("ReviewAnalytics", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, brand={self.brand}, model_family={self.model_family})>"