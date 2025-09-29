from sqlalchemy import Column, String, Integer, DECIMAL, TIMESTAMP, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Variant(Base):
    __tablename__ = "variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_sku = Column(String(100), unique=True, nullable=False)

    # Processor specifications
    processor = Column(String(255))
    processor_family = Column(String(100), index=True)
    processor_speed = Column(String(50))

    # Memory specifications
    memory = Column(String(100))
    memory_size = Column(Integer, index=True)  # Size in GB
    memory_type = Column(String(50))

    # Storage specifications
    storage = Column(String(100))
    storage_size = Column(Integer, index=True)  # Size in GB
    storage_type = Column(String(50), index=True)

    # Display specifications
    display = Column(String(100))
    display_size = Column(DECIMAL(4, 2))  # Size in inches
    display_resolution = Column(String(50))

    # Graphics and other specs
    graphics = Column(String(255))
    additional_features = Column(JSON, default=dict)

    # Pricing and availability
    price = Column(DECIMAL(10, 2), index=True)
    availability = Column(String(50))

    # For deduplication
    configuration_hash = Column(String(64), unique=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="variants")
    price_history = relationship("PriceHistory", back_populates="variant", cascade="all, delete-orphan")
    variant_offers = relationship("ProductOffer", back_populates="variant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Variant(id={self.id}, sku={self.variant_sku}, processor={self.processor})>"