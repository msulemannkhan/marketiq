from sqlalchemy import Column, String, Integer, DECIMAL, Text, TIMESTAMP, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ProductConfiguration(Base):
    """Enhanced product model for product_configurations.json data"""
    __tablename__ = "product_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Base Product Identification
    brand = Column(String(50), nullable=False, index=True)  # HP, Lenovo
    model_family = Column(String(100), nullable=False, index=True)  # ProBook 460, ThinkPad E14
    product_line = Column(String(100), index=True)  # G11, Gen 5

    # Base Product URLs and Sources
    base_url = Column(Text, nullable=False)
    pdf_spec_url = Column(Text)

    # Collection Metadata
    variants_total = Column(Integer, default=0)
    collected_at = Column(TIMESTAMP, nullable=False)
    data_source = Column(String(100), default="product_configurations")

    # JSON Storage for complex data
    base_product_data = Column(JSON, default=dict)  # Full base product info
    raw_data = Column(JSON, default=dict)  # Complete raw data for reference

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    configuration_variants = relationship("ConfigurationVariant", back_populates="product_configuration", cascade="all, delete-orphan")
    care_packages = relationship("CarePackage", back_populates="product_configuration", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductConfiguration(id={self.id}, brand={self.brand}, model_family={self.model_family})>"


class ConfigurationVariant(Base):
    """Enhanced variant model with all configuration details"""
    __tablename__ = "configuration_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_configuration_id = Column(UUID(as_uuid=True), ForeignKey("product_configurations.id", ondelete="CASCADE"), nullable=False)

    # Variant Identification
    variant_id = Column(String(50), nullable=False)  # Variant_001, Variant_002
    variant_sku = Column(String(100), nullable=False, index=True)  # A3RG1UA, A3RF5UA
    variant_url = Column(Text, nullable=False)

    # Configuration Sequence (for variant navigation)
    configuration_sequence = Column(JSON, default=list)  # ["14\"", "Intel Core Ultra 5 125U"]

    # PDP Summary (Product Detail Page info)
    title = Column(String(500))
    usage_label = Column(String(100))  # "ENERGY STAR | Business"
    rating = Column(DECIMAL(3, 2))  # 4.3
    review_count = Column(Integer)  # 118

    # Pricing Information
    msrp_label = Column(String(50))  # "MSRP"
    list_price = Column(DECIMAL(10, 2))  # 3489.00
    sale_price = Column(DECIMAL(10, 2))  # 1299.00
    discount_percentage = Column(Integer)  # 62
    savings_amount = Column(DECIMAL(10, 2))  # 2190.00

    # Stock and Delivery
    stock_status = Column(String(50))  # "In Stock"
    delivery_info = Column(String(200))  # "Ships on Sep. 18, 25"
    stock_icon = Column(String(50))  # "present"

    # Hero Snapshot Data
    offers = Column(ARRAY(Text), default=list)  # ["FREE Storewide Shipping", ...]
    rewards_badge = Column(String(100))  # "3% back in HP Rewards"
    sustainability_badge = Column(String(100))  # "Engineered for Sustainability"
    add_to_compare = Column(Boolean, default=False)

    # Technical Specifications (extracted from tech_specs JSON)
    operating_system = Column(String(100))
    processor_family = Column(String(100))
    processor = Column(String(500))
    graphics = Column(Text)
    memory = Column(String(100))
    memory_slots = Column(String(50))
    internal_drive = Column(String(200))
    display = Column(Text)

    # Additional Specs
    external_io_ports = Column(Text)
    audio_features = Column(Text)
    webcam = Column(String(200))
    keyboard = Column(Text)
    pointing_device = Column(Text)
    wireless_technology = Column(Text)
    network_interface = Column(String(200))
    power_supply = Column(String(200))
    battery = Column(String(200))
    color = Column(String(100))
    fingerprint_reader = Column(String(100))
    energy_efficiency = Column(String(200))
    dimensions = Column(String(200))
    weight = Column(String(100))
    warranty = Column(Text)

    # Software and Management
    security_software_license = Column(Text)
    software_included = Column(Text)
    manageability_features = Column(Text)
    security_management = Column(Text)
    support_service_included = Column(Text)
    sustainable_impact_specs = Column(Text)

    # Full JSON storage for complex nested data
    pdp_summary_data = Column(JSON, default=dict)
    hero_snapshot_data = Column(JSON, default=dict)
    tech_specs_data = Column(JSON, default=dict)
    cto_selected = Column(JSON, default=dict)  # Configuration-to-Order selected options

    # Timestamps
    data_timestamp = Column(TIMESTAMP)  # From source data
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    product_configuration = relationship("ProductConfiguration", back_populates="configuration_variants")
    variant_offers = relationship("VariantOffer", back_populates="configuration_variant", cascade="all, delete-orphan")
    price_snapshots = relationship("PriceSnapshot", back_populates="configuration_variant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConfigurationVariant(id={self.id}, variant_id={self.variant_id}, sku={self.variant_sku})>"


class CarePackage(Base):
    """Care packages and warranty options"""
    __tablename__ = "care_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_configuration_id = Column(UUID(as_uuid=True), ForeignKey("product_configurations.id", ondelete="CASCADE"), nullable=False)

    tier = Column(String(50), nullable=False)  # Standard, Essential, Premium, Premium+
    description = Column(Text, nullable=False)
    sale_price = Column(DECIMAL(10, 2))  # NULL for standard, prices for others

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product_configuration = relationship("ProductConfiguration", back_populates="care_packages")

    def __repr__(self):
        return f"<CarePackage(id={self.id}, tier={self.tier}, price={self.sale_price})>"


class VariantOffer(Base):
    """Specific offers for variants"""
    __tablename__ = "variant_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_variant_id = Column(UUID(as_uuid=True), ForeignKey("configuration_variants.id", ondelete="CASCADE"), nullable=False)

    offer_text = Column(Text, nullable=False)
    offer_type = Column(String(100))  # "shipping", "discount", "bundle"
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    configuration_variant = relationship("ConfigurationVariant", back_populates="variant_offers")

    def __repr__(self):
        return f"<VariantOffer(id={self.id}, offer_text={self.offer_text[:50]})>"


class PriceSnapshot(Base):
    """Historical price tracking for variants"""
    __tablename__ = "price_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_variant_id = Column(UUID(as_uuid=True), ForeignKey("configuration_variants.id", ondelete="CASCADE"), nullable=False)

    # Price data
    list_price = Column(DECIMAL(10, 2), nullable=False)
    sale_price = Column(DECIMAL(10, 2), nullable=False)
    discount_percentage = Column(Integer)
    savings_amount = Column(DECIMAL(10, 2))

    # Context
    stock_status = Column(String(50))
    delivery_info = Column(String(200))
    snapshot_date = Column(TIMESTAMP, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    configuration_variant = relationship("ConfigurationVariant", back_populates="price_snapshots")

    def __repr__(self):
        return f"<PriceSnapshot(id={self.id}, sale_price={self.sale_price}, snapshot_date={self.snapshot_date})>"