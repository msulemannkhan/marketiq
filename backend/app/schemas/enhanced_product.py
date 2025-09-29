from pydantic import BaseModel, UUID4, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


class EnhancedProductBase(BaseModel):
    brand: str = Field(..., max_length=50)
    model_series: str = Field(..., max_length=100)
    model_generation: Optional[str] = Field(None, max_length=50)
    full_title: str = Field(..., max_length=500)
    product_url: str

    usage_category: Optional[str] = Field(None, max_length=100)
    energy_star: bool = False
    sustainability_certified: bool = False

    base_sku: Optional[str] = Field(None, max_length=50)
    base_list_price: Optional[Decimal] = Field(None, ge=0)
    base_sale_price: Optional[Decimal] = Field(None, ge=0)
    base_discount_percentage: Optional[int] = Field(None, ge=0, le=100)

    average_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    total_reviews: Optional[int] = Field(None, ge=0)


class EnhancedProductCreate(EnhancedProductBase):
    scraped_at: datetime
    data_version: str = "2.0"


class EnhancedProductResponse(EnhancedProductBase):
    id: UUID4
    scraped_at: datetime
    variants_count: int = 0
    data_version: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnhancedVariantBase(BaseModel):
    variant_id: str = Field(..., max_length=50)
    sku: str = Field(..., max_length=50)
    variant_url: str

    # Pricing
    list_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    savings_amount: Optional[Decimal] = Field(None, ge=0)

    # Stock
    stock_status: Optional[str] = Field(None, max_length=50)
    estimated_ship_days: Optional[int] = Field(None, ge=0)

    # Core specs
    processor_brand: Optional[str] = Field(None, max_length=50)
    processor_family: Optional[str] = Field(None, max_length=100)
    processor_model: Optional[str] = Field(None, max_length=200)
    processor_cores: Optional[int] = Field(None, ge=1)
    processor_threads: Optional[int] = Field(None, ge=1)

    memory_size_gb: Optional[int] = Field(None, ge=1)
    memory_type: Optional[str] = Field(None, max_length=20)
    storage_size_gb: Optional[int] = Field(None, ge=1)
    storage_type: Optional[str] = Field(None, max_length=20)

    display_size_inches: Optional[int] = Field(None, ge=10, le=20)
    display_touch: bool = False

    operating_system: Optional[str] = Field(None, max_length=100)


class EnhancedVariantCreate(EnhancedVariantBase):
    product_id: UUID4

    # Extended technical specs
    processor_base_speed: Optional[str] = Field(None, max_length=20)
    processor_max_speed: Optional[str] = Field(None, max_length=20)
    processor_cache: Optional[str] = Field(None, max_length=20)

    memory_speed: Optional[str] = Field(None, max_length=30)
    memory_slots: Optional[str] = Field(None, max_length=20)
    memory_configuration: Optional[str] = Field(None, max_length=50)

    storage_interface: Optional[str] = Field(None, max_length=50)

    display_resolution: Optional[str] = Field(None, max_length=20)
    display_resolution_standard: Optional[str] = Field(None, max_length=20)
    display_panel_type: Optional[str] = Field(None, max_length=20)
    display_brightness_nits: Optional[int] = Field(None, ge=100)
    display_color_gamut: Optional[str] = Field(None, max_length=30)

    graphics_integrated: Optional[str] = Field(None, max_length=200)
    graphics_discrete: Optional[str] = Field(None, max_length=200)

    # Physical specs
    width_inches: Optional[float] = Field(None, ge=0)
    depth_inches: Optional[float] = Field(None, ge=0)
    height_front_inches: Optional[float] = Field(None, ge=0)
    height_rear_inches: Optional[float] = Field(None, ge=0)
    weight_lbs: Optional[float] = Field(None, ge=0)

    # Connectivity
    usb_c_ports: Optional[int] = Field(None, ge=0)
    usb_a_ports: Optional[int] = Field(None, ge=0)
    hdmi_ports: Optional[int] = Field(None, ge=0)
    ethernet_port: bool = False
    audio_jack: bool = False
    wifi_standard: Optional[str] = Field(None, max_length=50)
    bluetooth_version: Optional[str] = Field(None, max_length=20)

    # Features
    fingerprint_reader: bool = False
    backlit_keyboard: bool = False
    touchpad_type: Optional[str] = Field(None, max_length=100)
    webcam_resolution: Optional[str] = Field(None, max_length=20)

    # Power
    battery_capacity_wh: Optional[int] = Field(None, ge=0)
    battery_cells: Optional[int] = Field(None, ge=1)
    power_adapter_watts: Optional[int] = Field(None, ge=0)

    color: Optional[str] = Field(None, max_length=100)
    warranty_years: Optional[int] = Field(None, ge=0)

    # Raw data preservation
    raw_tech_specs: Optional[Dict[str, Any]] = Field(default_factory=dict)
    raw_pdp_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    raw_hero_snapshot: Optional[Dict[str, Any]] = Field(default_factory=dict)
    configuration_path: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    variant_scraped_at: Optional[datetime] = None


class EnhancedVariantResponse(EnhancedVariantBase):
    id: UUID4
    product_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnhancedCarePackageBase(BaseModel):
    tier: str = Field(..., max_length=50)
    description: str
    sale_price: Optional[Decimal] = Field(None, ge=0)
    duration_years: Optional[int] = Field(None, ge=0)


class EnhancedCarePackageCreate(EnhancedCarePackageBase):
    enhanced_product_id: UUID4


class EnhancedCarePackageResponse(EnhancedCarePackageBase):
    id: UUID4
    enhanced_product_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnhancedProductOfferBase(BaseModel):
    offer_text: str
    offer_type: Optional[str] = Field(None, max_length=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True


class EnhancedProductOfferCreate(EnhancedProductOfferBase):
    enhanced_product_id: UUID4


class EnhancedProductOfferResponse(EnhancedProductOfferBase):
    id: UUID4
    enhanced_product_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnhancedPriceHistoryBase(BaseModel):
    list_price: Decimal = Field(..., ge=0)
    sale_price: Decimal = Field(..., ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    savings_amount: Optional[Decimal] = Field(None, ge=0)
    stock_status: Optional[str] = Field(None, max_length=50)
    estimated_ship_days: Optional[int] = Field(None, ge=0)
    scraped_at: datetime
    source_url: Optional[str] = None


class EnhancedPriceHistoryCreate(EnhancedPriceHistoryBase):
    variant_id: UUID4


class EnhancedPriceHistoryResponse(EnhancedPriceHistoryBase):
    id: UUID4
    variant_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Complex response schemas
class EnhancedProductDetail(EnhancedProductResponse):
    """Detailed product with all relationships"""
    variants: List[EnhancedVariantResponse] = Field(default_factory=list)
    enhanced_care_packages: List[EnhancedCarePackageResponse] = Field(default_factory=list)
    enhanced_product_offers: List[EnhancedProductOfferResponse] = Field(default_factory=list)


class EnhancedVariantDetail(EnhancedVariantResponse):
    """Detailed variant with price history"""
    price_history: List[EnhancedPriceHistoryResponse] = Field(default_factory=list)


# Search and filter schemas
class EnhancedProductFilter(BaseModel):
    """Filter schema for enhanced product search"""
    brand: Optional[str] = None
    model_series: Optional[str] = None
    processor_brand: Optional[str] = None
    processor_cores_min: Optional[int] = Field(None, ge=1)
    memory_size_min: Optional[int] = Field(None, ge=1)
    storage_size_min: Optional[int] = Field(None, ge=1)
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)
    display_size_min: Optional[int] = Field(None, ge=10)
    display_touch: Optional[bool] = None
    fingerprint_reader: Optional[bool] = None
    in_stock_only: Optional[bool] = None


class EnhancedProductSearch(BaseModel):
    """Search response with pagination"""
    products: List[EnhancedProductResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
    filters_applied: EnhancedProductFilter


# Analytics schemas
class EnhancedProductStats(BaseModel):
    """Statistics for enhanced products"""
    total_products: int = 0
    total_variants: int = 0
    brands: List[str] = Field(default_factory=list)
    avg_variants_per_product: float = 0.0
    price_range: Dict[str, float] = Field(default_factory=dict)
    latest_scrape_date: Optional[datetime] = None


# Import status schema
class DataImportStats(BaseModel):
    """Statistics for data import operations"""
    total_products_imported: int = 0
    total_variants_imported: int = 0
    last_import_date: Optional[datetime] = None
    data_quality_score: float = 0.0
    brands_available: List[str] = Field(default_factory=list)