from sqlalchemy import Column, String, Integer, DECIMAL, Text, TIMESTAMP, JSON, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class EnhancedProduct(Base):
    """Enhanced product model with optimized structure for HP scraped data"""
    __tablename__ = "enhanced_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Product Info
    brand = Column(String(50), nullable=False, index=True)  # HP, Lenovo
    model_series = Column(String(100), nullable=False, index=True)  # ProBook 460, ThinkPad E14
    model_generation = Column(String(50), index=True)  # G11, Gen 5
    full_title = Column(String(500), nullable=False)  # Full product title
    product_url = Column(Text, nullable=False, unique=True)

    # Business/Usage Classification
    usage_category = Column(String(100))  # Business, Consumer, Gaming
    energy_star = Column(Boolean, default=False)
    sustainability_certified = Column(Boolean, default=False)

    # Base Configuration (from base product)
    base_sku = Column(String(50))
    base_list_price = Column(DECIMAL(10, 2))
    base_sale_price = Column(DECIMAL(10, 2))
    base_discount_percentage = Column(Integer)

    # Review Data
    average_rating = Column(DECIMAL(3, 2))  # 4.3
    total_reviews = Column(Integer)

    # Data Management
    scraped_at = Column(TIMESTAMP, nullable=False)
    variants_count = Column(Integer, default=0)
    data_version = Column(String(20), default="1.0")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    variants = relationship("EnhancedVariant", back_populates="product", cascade="all, delete-orphan")
    enhanced_care_packages = relationship("EnhancedCarePackage", back_populates="enhanced_product", cascade="all, delete-orphan")
    enhanced_product_offers = relationship("EnhancedProductOffer", back_populates="enhanced_product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EnhancedProduct(brand={self.brand}, model_series={self.model_series})>"


class EnhancedVariant(Base):
    """Enhanced variant model with structured technical specifications"""
    __tablename__ = "enhanced_variants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("enhanced_products.id", ondelete="CASCADE"), nullable=False)

    # Variant Identification
    variant_id = Column(String(50), nullable=False, index=True)  # Variant_001
    sku = Column(String(50), nullable=False, unique=True)  # A3RG1UA
    variant_url = Column(Text, nullable=False)

    # Configuration Sequence (for navigation)
    configuration_path = Column(JSON)  # Structured path data

    # Pricing (structured)
    list_price = Column(DECIMAL(10, 2), index=True)
    sale_price = Column(DECIMAL(10, 2), index=True)
    discount_percentage = Column(Integer)
    savings_amount = Column(DECIMAL(10, 2))

    # Stock & Availability
    stock_status = Column(String(50), index=True)  # "In Stock", "Out of Stock"
    estimated_ship_days = Column(Integer)  # Extracted from delivery info

    # Processor Specifications (structured)
    processor_brand = Column(String(50), index=True)  # Intel, AMD
    processor_family = Column(String(100), index=True)  # Intel Core Ultra 7
    processor_model = Column(String(200))  # Intel Core Ultra 7 155H
    processor_base_speed = Column(String(20))  # "2.4 GHz"
    processor_max_speed = Column(String(20))  # "4.8 GHz"
    processor_cores = Column(Integer, index=True)  # 16
    processor_threads = Column(Integer)  # 22
    processor_cache = Column(String(20))  # "24 MB"

    # Memory Specifications (structured)
    memory_size_gb = Column(Integer, index=True)  # 32
    memory_type = Column(String(20), index=True)  # DDR5
    memory_speed = Column(String(30))  # "5600 MT/s"
    memory_slots = Column(String(20))  # "2 SODIMM"
    memory_configuration = Column(String(50))  # "2 x 16 GB"

    # Storage Specifications (structured)
    storage_size_gb = Column(Integer, index=True)  # 1000
    storage_type = Column(String(20), index=True)  # SSD, HDD
    storage_interface = Column(String(50))  # "PCIe NVMe"

    # Display Specifications (structured)
    display_size_inches = Column(Integer, index=True)  # 16
    display_resolution = Column(String(20))  # "1920x1200"
    display_resolution_standard = Column(String(20))  # "WUXGA"
    display_touch = Column(Boolean, default=False, index=True)
    display_panel_type = Column(String(20))  # "IPS"
    display_brightness_nits = Column(Integer)  # 300
    display_color_gamut = Column(String(30))  # "45% NTSC"

    # Graphics
    graphics_integrated = Column(String(200))  # Intel Arc Graphics
    graphics_discrete = Column(String(200))  # NVIDIA GeForce RTX 2050

    # Physical Specifications
    width_inches = Column(Float)  # 14.15
    depth_inches = Column(Float)  # 9.88
    height_front_inches = Column(Float)  # 0.43
    height_rear_inches = Column(Float)  # 0.67
    weight_lbs = Column(Float, index=True)  # 3.85

    # Connectivity
    usb_c_ports = Column(Integer)
    usb_a_ports = Column(Integer)
    hdmi_ports = Column(Integer)
    ethernet_port = Column(Boolean, default=False)
    audio_jack = Column(Boolean, default=False)

    # Features
    fingerprint_reader = Column(Boolean, default=False, index=True)
    backlit_keyboard = Column(Boolean, default=False, index=True)
    touchpad_type = Column(String(100))
    webcam_resolution = Column(String(20))  # "5 MP"
    wifi_standard = Column(String(50))  # "Wi-Fi 6E"
    bluetooth_version = Column(String(20))  # "5.3"

    # Power & Battery
    battery_capacity_wh = Column(Integer)  # 56
    battery_cells = Column(Integer)  # 3
    power_adapter_watts = Column(Integer)  # 100

    # Operating System
    operating_system = Column(String(100))  # "Windows 11 Pro"

    # Color & Design
    color = Column(String(100))  # "Pike silver aluminum"

    # Warranty
    warranty_years = Column(Integer)  # 1

    # Raw data preservation
    raw_tech_specs = Column(JSON)  # Complete original tech_specs
    raw_pdp_summary = Column(JSON)  # Complete original pdp_summary
    raw_hero_snapshot = Column(JSON)  # Complete original hero_snapshot

    # Timestamps
    variant_scraped_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product = relationship("EnhancedProduct", back_populates="variants")
    price_history = relationship("EnhancedPriceHistory", back_populates="variant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EnhancedVariant(sku={self.sku}, processor={self.processor_model})>"


class EnhancedPriceHistory(Base):
    """Price tracking with enhanced metadata"""
    __tablename__ = "enhanced_price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("enhanced_variants.id", ondelete="CASCADE"), nullable=False)

    # Price data
    list_price = Column(DECIMAL(10, 2), nullable=False)
    sale_price = Column(DECIMAL(10, 2), nullable=False)
    discount_percentage = Column(Integer)
    savings_amount = Column(DECIMAL(10, 2))

    # Context
    stock_status = Column(String(50))
    estimated_ship_days = Column(Integer)

    # Data source tracking
    scraped_at = Column(TIMESTAMP, nullable=False)
    source_url = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    variant = relationship("EnhancedVariant", back_populates="price_history")

    def __repr__(self):
        return f"<EnhancedPriceHistory(sale_price={self.sale_price}, scraped_at={self.scraped_at})>"


class TechnicalSpecificationIndex(Base):
    """Searchable index of all technical specifications for AI/LLM queries"""
    __tablename__ = "tech_spec_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("enhanced_variants.id", ondelete="CASCADE"), nullable=False)

    # Specification category
    spec_category = Column(String(100), nullable=False, index=True)  # processor, memory, storage, etc.
    spec_key = Column(String(100), nullable=False, index=True)  # cores, cache, speed, etc.
    spec_value = Column(Text, nullable=False)  # The actual value
    spec_value_numeric = Column(Float)  # Numeric version if applicable
    spec_value_unit = Column(String(20))  # GB, GHz, inches, etc.

    # Search optimization
    searchable_text = Column(Text)  # Combined text for full-text search

    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<TechSpecIndex(category={self.spec_category}, key={self.spec_key})>"


class ProductComparisonCache(Base):
    """Cache for frequently compared products to optimize performance"""
    __tablename__ = "product_comparison_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Products being compared (sorted for consistency)
    product_ids = Column(JSON, nullable=False)  # Array of UUIDs
    comparison_hash = Column(String(64), nullable=False, unique=True, index=True)

    # Cached comparison data
    comparison_result = Column(JSON, nullable=False)

    # Cache metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    accessed_count = Column(Integer, default=1)
    last_accessed = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<ProductComparisonCache(hash={self.comparison_hash})>"


class EnhancedCarePackage(Base):
    """Enhanced care packages for products"""
    __tablename__ = "enhanced_care_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enhanced_product_id = Column(UUID(as_uuid=True), ForeignKey("enhanced_products.id", ondelete="CASCADE"), nullable=False)

    tier = Column(String(50), nullable=False)  # Standard, Essential, Premium, Premium+
    description = Column(Text, nullable=False)
    sale_price = Column(DECIMAL(10, 2))  # NULL for standard, prices for others
    duration_years = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    enhanced_product = relationship("EnhancedProduct", back_populates="enhanced_care_packages")

    def __repr__(self):
        return f"<EnhancedCarePackage(tier={self.tier}, price={self.sale_price})>"


class EnhancedProductOffer(Base):
    """Enhanced product offers"""
    __tablename__ = "enhanced_product_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enhanced_product_id = Column(UUID(as_uuid=True), ForeignKey("enhanced_products.id", ondelete="CASCADE"), nullable=False)

    offer_text = Column(Text, nullable=False)
    offer_type = Column(String(100))  # shipping, discount, bundle
    discount_amount = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    enhanced_product = relationship("EnhancedProduct", back_populates="enhanced_product_offers")

    def __repr__(self):
        return f"<EnhancedProductOffer(type={self.offer_type}, text={self.offer_text[:50]})>"