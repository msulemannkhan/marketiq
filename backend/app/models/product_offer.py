from sqlalchemy import Column, String, Text, DECIMAL, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ProductOffer(Base):
    __tablename__ = "product_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=True)
    badge = Column(String(100))
    offer_text = Column(Text, nullable=False)
    offer_type = Column(String(50))  # DISCOUNT, FREE_SHIPPING, BUNDLE, etc.
    discount_amount = Column(DECIMAL(10, 2))
    discount_percentage = Column(DECIMAL(5, 2))
    promo_code = Column(String(50))
    valid_from = Column(TIMESTAMP)
    valid_until = Column(TIMESTAMP)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="product_offers")
    variant = relationship("Variant", back_populates="variant_offers")

    def __repr__(self):
        return f"<ProductOffer(id={self.id}, product_id={self.product_id}, offer_type={self.offer_type})>"