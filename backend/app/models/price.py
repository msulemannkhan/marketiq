from sqlalchemy import Column, DECIMAL, Date, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id", ondelete="CASCADE"), nullable=False)

    price = Column(DECIMAL(10, 2), nullable=False)
    captured_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    variant = relationship("Variant", back_populates="price_history")

    # Composite index for efficient querying
    __table_args__ = (
        Index('idx_price_history_variant_date', 'variant_id', 'captured_date'),
    )

    def __repr__(self):
        return f"<PriceHistory(variant_id={self.variant_id}, price={self.price}, date={self.captured_date})>"