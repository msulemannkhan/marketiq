from pydantic import BaseModel, UUID4, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# Base Schemas
class ProductConfigurationBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    brand: str = Field(..., max_length=50, description="Brand name (HP, Lenovo)")
    model_family: str = Field(..., max_length=100, description="Model family (ProBook 460, ThinkPad E14)")
    product_line: Optional[str] = Field(None, max_length=100, description="Product line (G11, Gen 5)")
    base_url: str = Field(..., description="Base product URL")
    pdf_spec_url: Optional[str] = Field(None, description="PDF specification URL")
    variants_total: int = Field(default=0, ge=0, description="Total number of variants")
    data_source: str = Field(default="product_configurations", max_length=100)


class ProductConfigurationCreate(ProductConfigurationBase):
    collected_at: datetime = Field(..., description="Data collection timestamp")
    base_product_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProductConfigurationUpdate(BaseModel):
    brand: Optional[str] = Field(None, max_length=50)
    model_family: Optional[str] = Field(None, max_length=100)
    product_line: Optional[str] = Field(None, max_length=100)
    base_url: Optional[str] = None
    pdf_spec_url: Optional[str] = None
    variants_total: Optional[int] = Field(None, ge=0)
    data_source: Optional[str] = Field(None, max_length=100)
    base_product_data: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None


class ProductConfigurationResponse(ProductConfigurationBase):
    id: UUID4
    collected_at: datetime
    base_product_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Configuration Variant Schemas
class ConfigurationVariantBase(BaseModel):
    variant_id: str = Field(..., max_length=50, description="Variant identifier")
    variant_sku: str = Field(..., max_length=100, description="Variant SKU")
    variant_url: str = Field(..., description="Variant URL")
    configuration_sequence: Optional[List[str]] = Field(default_factory=list)

    # PDP Summary
    title: Optional[str] = Field(None, max_length=500)
    usage_label: Optional[str] = Field(None, max_length=100)
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)

    # Pricing
    msrp_label: Optional[str] = Field(None, max_length=50)
    list_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    savings_amount: Optional[Decimal] = Field(None, ge=0)

    # Stock and Delivery
    stock_status: Optional[str] = Field(None, max_length=50)
    delivery_info: Optional[str] = Field(None, max_length=200)
    stock_icon: Optional[str] = Field(None, max_length=50)

    # Hero Snapshot
    offers: Optional[List[str]] = Field(default_factory=list)
    rewards_badge: Optional[str] = Field(None, max_length=100)
    sustainability_badge: Optional[str] = Field(None, max_length=100)
    add_to_compare: bool = Field(default=False)


class ConfigurationVariantCreate(ConfigurationVariantBase):
    product_configuration_id: UUID4

    # Technical Specs (extracted from tech_specs)
    operating_system: Optional[str] = Field(None, max_length=100)
    processor_family: Optional[str] = Field(None, max_length=100)
    processor: Optional[str] = Field(None, max_length=500)
    graphics: Optional[str] = None
    memory: Optional[str] = Field(None, max_length=100)
    memory_slots: Optional[str] = Field(None, max_length=50)
    internal_drive: Optional[str] = Field(None, max_length=200)
    display: Optional[str] = None

    # Additional technical fields
    external_io_ports: Optional[str] = None
    audio_features: Optional[str] = None
    webcam: Optional[str] = Field(None, max_length=200)
    keyboard: Optional[str] = None
    pointing_device: Optional[str] = None
    wireless_technology: Optional[str] = None
    network_interface: Optional[str] = Field(None, max_length=200)
    power_supply: Optional[str] = Field(None, max_length=200)
    battery: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=100)
    fingerprint_reader: Optional[str] = Field(None, max_length=100)
    energy_efficiency: Optional[str] = Field(None, max_length=200)
    dimensions: Optional[str] = Field(None, max_length=200)
    weight: Optional[str] = Field(None, max_length=100)
    warranty: Optional[str] = None

    # Software and Management
    security_software_license: Optional[str] = None
    software_included: Optional[str] = None
    manageability_features: Optional[str] = None
    security_management: Optional[str] = None
    support_service_included: Optional[str] = None
    sustainable_impact_specs: Optional[str] = None

    # JSON data
    pdp_summary_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hero_snapshot_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    tech_specs_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    cto_selected: Optional[Dict[str, Any]] = Field(default_factory=dict)

    data_timestamp: Optional[datetime] = None


class ConfigurationVariantUpdate(BaseModel):
    variant_id: Optional[str] = Field(None, max_length=50)
    variant_sku: Optional[str] = Field(None, max_length=100)
    variant_url: Optional[str] = None
    title: Optional[str] = Field(None, max_length=500)
    usage_label: Optional[str] = Field(None, max_length=100)
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)
    list_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    stock_status: Optional[str] = Field(None, max_length=50)
    delivery_info: Optional[str] = Field(None, max_length=200)


class ConfigurationVariantResponse(ConfigurationVariantBase):
    id: UUID4
    product_configuration_id: UUID4

    # Technical specs
    operating_system: Optional[str] = None
    processor_family: Optional[str] = None
    processor: Optional[str] = None
    graphics: Optional[str] = None
    memory: Optional[str] = None
    display: Optional[str] = None

    # Additional fields for response
    color: Optional[str] = None
    weight: Optional[str] = None
    dimensions: Optional[str] = None

    data_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Care Package Schemas
class CarePackageBase(BaseModel):
    tier: str = Field(..., max_length=50, description="Care package tier")
    description: str = Field(..., description="Care package description")
    sale_price: Optional[Decimal] = Field(None, ge=0)


class CarePackageCreate(CarePackageBase):
    product_configuration_id: UUID4


class CarePackageResponse(CarePackageBase):
    id: UUID4
    product_configuration_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Variant Offer Schemas
class VariantOfferBase(BaseModel):
    offer_text: str = Field(..., description="Offer description")
    offer_type: Optional[str] = Field(None, max_length=100, description="Type of offer")
    is_active: bool = Field(default=True)


class VariantOfferCreate(VariantOfferBase):
    configuration_variant_id: UUID4


class VariantOfferResponse(VariantOfferBase):
    id: UUID4
    configuration_variant_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Price Snapshot Schemas
class PriceSnapshotBase(BaseModel):
    list_price: Decimal = Field(..., ge=0)
    sale_price: Decimal = Field(..., ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    savings_amount: Optional[Decimal] = Field(None, ge=0)
    stock_status: Optional[str] = Field(None, max_length=50)
    delivery_info: Optional[str] = Field(None, max_length=200)
    snapshot_date: datetime


class PriceSnapshotCreate(PriceSnapshotBase):
    configuration_variant_id: UUID4


class PriceSnapshotResponse(PriceSnapshotBase):
    id: UUID4
    configuration_variant_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Complex Response Schemas
class ConfigurationVariantDetail(ConfigurationVariantResponse):
    """Detailed variant with relationships"""
    variant_offers: List[VariantOfferResponse] = Field(default_factory=list)
    price_snapshots: List[PriceSnapshotResponse] = Field(default_factory=list)


class ProductConfigurationDetail(ProductConfigurationResponse):
    """Detailed product configuration with relationships"""
    configuration_variants: List[ConfigurationVariantDetail] = Field(default_factory=list)
    care_packages: List[CarePackageResponse] = Field(default_factory=list)


# Bulk Import Schemas
class BulkImportRequest(BaseModel):
    """Schema for bulk import from product_configurations.json"""
    file_path: Optional[str] = Field(None, description="Path to JSON file")
    json_data: Optional[Dict[str, Any]] = Field(None, description="Direct JSON data")
    override_existing: bool = Field(default=False, description="Whether to override existing data")

    @field_validator('file_path', 'json_data')
    @classmethod
    def validate_source(cls, v, info):
        # Ensure at least one source is provided
        if info.field_name == 'json_data' and v is None:
            file_path = info.data.get('file_path')
            if file_path is None:
                raise ValueError('Either file_path or json_data must be provided')
        return v


class BulkImportResponse(BaseModel):
    """Response for bulk import operations"""
    success: bool
    products_created: int = 0
    variants_created: int = 0
    care_packages_created: int = 0
    offers_created: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time_seconds: float = 0.0


# Search and Filter Schemas
class ConfigurationVariantFilter(BaseModel):
    """Filter schema for variant search"""
    brand: Optional[str] = None
    model_family: Optional[str] = None
    processor_family: Optional[str] = None
    memory_size_min: Optional[str] = None  # e.g., "16 GB"
    memory_size_max: Optional[str] = None
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)
    display_size: Optional[str] = None  # e.g., "16\""
    stock_status: Optional[str] = None
    has_discount: Optional[bool] = None


class ConfigurationVariantSearch(BaseModel):
    """Search response with pagination"""
    variants: List[ConfigurationVariantResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
    filters_applied: ConfigurationVariantFilter


# Analytics Schemas
class ProductConfigurationStats(BaseModel):
    """Statistics for product configurations"""
    model_config = ConfigDict(protected_namespaces=())

    total_products: int = 0
    total_variants: int = 0
    brands_count: int = 0
    model_families_count: int = 0
    average_variants_per_product: float = 0.0
    price_range: Dict[str, Decimal] = Field(default_factory=dict)  # min, max, average
    latest_collection_date: Optional[datetime] = None
    data_freshness_hours: Optional[float] = None


# Export Schemas
class ProductConfigurationExport(BaseModel):
    """Export schema for external systems"""
    product_configuration: ProductConfigurationResponse
    variants: List[ConfigurationVariantResponse]
    care_packages: List[CarePackageResponse]
    export_timestamp: datetime
    export_format: str = "json"