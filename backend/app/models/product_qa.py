from sqlalchemy import Column, String, Text, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ProductQA(Base):
    __tablename__ = "product_qa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    votes = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    author = Column(String(100))
    asked_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="qa_items")

    def __repr__(self):
        return f"<ProductQA(id={self.id}, product_id={self.product_id}, verified={self.verified})>"