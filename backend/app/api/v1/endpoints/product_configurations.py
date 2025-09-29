from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
import json
import time
from pathlib import Path

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.product_config import (
    ProductConfigurationResponse, ProductConfigurationCreate, ProductConfigurationUpdate,
    ProductConfigurationDetail, ConfigurationVariantResponse, ConfigurationVariantDetail,
    ConfigurationVariantFilter, ConfigurationVariantSearch, BulkImportRequest,
    BulkImportResponse, ProductConfigurationStats, ProductConfigurationExport
)
from app.crud.product_config import (
    ProductConfigurationCRUD, ConfigurationVariantCRUD, BulkProductConfigCRUD,
    ProductConfigAnalytics
)

router = APIRouter()


# Product Configuration Endpoints
@router.get("/configurations", response_model=List[ProductConfigurationResponse])
async def get_product_configurations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    model_family: Optional[str] = Query(None, description="Filter by model family"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all product configurations with optional filtering"""
    configurations = ProductConfigurationCRUD.get_all(
        db=db,
        skip=skip,
        limit=limit,
        brand=brand,
        model_family=model_family
    )
    return configurations


@router.get("/configurations/{configuration_id}", response_model=ProductConfigurationDetail)
async def get_product_configuration(
    configuration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific product configuration with all variants and care packages"""
    configuration = ProductConfigurationCRUD.get_with_variants(db, configuration_id)
    if not configuration:
        raise HTTPException(status_code=404, detail="Product configuration not found")
    return configuration


@router.post("/configurations", response_model=ProductConfigurationResponse)
async def create_product_configuration(
    configuration: ProductConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product configuration"""
    # Check if configuration already exists by URL
    existing = ProductConfigurationCRUD.get_by_url(db, configuration.base_url)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Product configuration already exists for URL: {configuration.base_url}"
        )

    return ProductConfigurationCRUD.create(db, configuration)


@router.put("/configurations/{configuration_id}", response_model=ProductConfigurationResponse)
async def update_product_configuration(
    configuration_id: str,
    configuration: ProductConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product configuration"""
    updated_config = ProductConfigurationCRUD.update(db, configuration_id, configuration)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Product configuration not found")
    return updated_config


@router.delete("/configurations/{configuration_id}")
async def delete_product_configuration(
    configuration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product configuration"""
    if not ProductConfigurationCRUD.delete(db, configuration_id):
        raise HTTPException(status_code=404, detail="Product configuration not found")
    return {"message": "Product configuration deleted successfully"}


# Configuration Variant Endpoints
@router.get("/variants", response_model=ConfigurationVariantSearch)
async def search_configuration_variants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    model_family: Optional[str] = Query(None, description="Filter by model family"),
    processor_family: Optional[str] = Query(None, description="Filter by processor family"),
    memory_size_min: Optional[str] = Query(None, description="Minimum memory size (e.g., '16 GB')"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    display_size: Optional[str] = Query(None, description="Display size (e.g., '16\"')"),
    stock_status: Optional[str] = Query(None, description="Stock status"),
    has_discount: Optional[bool] = Query(None, description="Has discount available"),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search configuration variants with advanced filtering"""
    filters = ConfigurationVariantFilter(
        brand=brand,
        model_family=model_family,
        processor_family=processor_family,
        memory_size_min=memory_size_min,
        price_min=price_min,
        price_max=price_max,
        display_size=display_size,
        stock_status=stock_status,
        has_discount=has_discount
    )

    variants = ConfigurationVariantCRUD.search_variants(
        db=db,
        filters=filters,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc
    )

    # Get total count for pagination
    total_variants = ConfigurationVariantCRUD.search_variants(
        db=db,
        filters=filters,
        skip=0,
        limit=10000  # Large number to get total count
    )

    return ConfigurationVariantSearch(
        variants=variants,
        total=len(total_variants),
        page=skip // limit + 1,
        page_size=limit,
        has_more=len(variants) == limit,
        filters_applied=filters
    )


@router.get("/variants/{variant_id}", response_model=ConfigurationVariantDetail)
async def get_configuration_variant(
    variant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific configuration variant with offers and price history"""
    variant = ConfigurationVariantCRUD.get_with_offers_and_prices(db, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Configuration variant not found")
    return variant


@router.get("/variants/{variant_id}/price-history")
async def get_variant_price_history(
    variant_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of price history"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price history for a configuration variant"""
    variant = ConfigurationVariantCRUD.get(db, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Configuration variant not found")

    price_history = ConfigurationVariantCRUD.get_price_trends(db, variant_id, days)

    # Calculate price trends
    if len(price_history) >= 2:
        latest_price = price_history[-1].sale_price
        oldest_price = price_history[0].sale_price
        price_change = latest_price - oldest_price
        price_change_percentage = (price_change / oldest_price * 100) if oldest_price > 0 else 0

        trend = "stable"
        if price_change_percentage > 5:
            trend = "increasing"
        elif price_change_percentage < -5:
            trend = "decreasing"
    else:
        trend = "unknown"
        price_change = 0
        price_change_percentage = 0

    return {
        "variant_id": variant_id,
        "price_history": price_history,
        "trend_analysis": {
            "trend": trend,
            "price_change": float(price_change),
            "price_change_percentage": round(price_change_percentage, 2),
            "data_points": len(price_history),
            "period_days": days
        }
    }


# Bulk Import Endpoints
@router.post("/configurations/import", response_model=BulkImportResponse)
async def import_product_configurations(
    import_request: BulkImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import product configurations from JSON data or file"""
    start_time = time.time()

    try:
        # Get JSON data either from request or file
        if import_request.json_data:
            json_data = import_request.json_data
        elif import_request.file_path:
            try:
                with open(import_request.file_path, 'r', encoding='utf-8') as file:
                    json_data = json.load(file)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"File not found: {import_request.file_path}")
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Either json_data or file_path must be provided")

        # Perform import
        result = BulkProductConfigCRUD.import_from_json(
            db=db,
            json_data=json_data,
            override_existing=import_request.override_existing
        )

        # Calculate processing time
        processing_time = time.time() - start_time
        result["processing_time_seconds"] = round(processing_time, 2)

        return BulkImportResponse(**result)

    except Exception as e:
        processing_time = time.time() - start_time
        return BulkImportResponse(
            success=False,
            errors=[f"Import failed: {str(e)}"],
            processing_time_seconds=round(processing_time, 2)
        )


@router.post("/configurations/import/file", response_model=BulkImportResponse)
async def import_from_uploaded_file(
    file: UploadFile = File(...),
    override_existing: bool = Query(False, description="Override existing configurations"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import product configurations from uploaded JSON file"""
    start_time = time.time()

    # Validate file type
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        # Read file content
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))

        # Perform import
        result = BulkProductConfigCRUD.import_from_json(
            db=db,
            json_data=json_data,
            override_existing=override_existing
        )

        # Calculate processing time
        processing_time = time.time() - start_time
        result["processing_time_seconds"] = round(processing_time, 2)

        return BulkImportResponse(**result)

    except json.JSONDecodeError as e:
        return BulkImportResponse(
            success=False,
            errors=[f"Invalid JSON file: {str(e)}"],
            processing_time_seconds=round(time.time() - start_time, 2)
        )
    except Exception as e:
        return BulkImportResponse(
            success=False,
            errors=[f"Import failed: {str(e)}"],
            processing_time_seconds=round(time.time() - start_time, 2)
        )


# Analytics and Statistics Endpoints
@router.get("/analytics/statistics", response_model=ProductConfigurationStats)
async def get_product_configuration_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive statistics for product configurations"""
    stats = ProductConfigAnalytics.get_statistics(db)
    return ProductConfigurationStats(**stats)


@router.get("/analytics/brand-comparison")
async def get_brand_comparison(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comparison statistics between brands"""
    return ProductConfigAnalytics.get_brand_comparison(db)


@router.get("/analytics/price-trends")
async def get_price_trends_analysis(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    model_family: Optional[str] = Query(None, description="Filter by model family"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price trends analysis across variants"""
    from sqlalchemy import and_

    # Build query based on filters
    query = db.query(
        ConfigurationVariant.variant_sku,
        ConfigurationVariant.title,
        ConfigurationVariant.sale_price,
        ConfigurationVariant.list_price,
        ConfigurationVariant.discount_percentage,
        ProductConfiguration.brand,
        ProductConfiguration.model_family
    ).join(ProductConfiguration)

    if brand:
        query = query.filter(ProductConfiguration.brand == brand)
    if model_family:
        query = query.filter(ProductConfiguration.model_family == model_family)

    variants = query.all()

    # Calculate overall statistics
    prices = [float(variant.sale_price) for variant in variants if variant.sale_price]
    discounts = [variant.discount_percentage for variant in variants if variant.discount_percentage]

    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
    else:
        avg_price = min_price = max_price = 0.0

    if discounts:
        avg_discount = sum(discounts) / len(discounts)
        max_discount = max(discounts)
    else:
        avg_discount = max_discount = 0.0

    return {
        "analysis_period_days": days,
        "total_variants_analyzed": len(variants),
        "price_statistics": {
            "average_price": round(avg_price, 2),
            "min_price": min_price,
            "max_price": max_price,
            "price_range": max_price - min_price
        },
        "discount_statistics": {
            "average_discount_percentage": round(avg_discount, 2),
            "max_discount_percentage": max_discount,
            "variants_with_discount": len([d for d in discounts if d > 0])
        },
        "brand_breakdown": {
            brand: len([v for v in variants if v.brand == brand])
            for brand in set(v.brand for v in variants)
        }
    }


# Export Endpoints
@router.get("/configurations/{configuration_id}/export", response_model=ProductConfigurationExport)
async def export_product_configuration(
    configuration_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export a product configuration with all related data"""
    from datetime import datetime

    configuration = ProductConfigurationCRUD.get_with_variants(db, configuration_id)
    if not configuration:
        raise HTTPException(status_code=404, detail="Product configuration not found")

    # Get care packages
    from app.crud.product_config import CarePackageCRUD
    care_packages = CarePackageCRUD.get_by_product_config(db, configuration_id)

    return ProductConfigurationExport(
        product_configuration=configuration,
        variants=configuration.configuration_variants,
        care_packages=care_packages,
        export_timestamp=datetime.utcnow(),
        export_format="json"
    )


# Health Check for Product Configurations
@router.get("/health")
async def health_check(
    db: Session = Depends(get_db)
):
    """Health check for product configuration service"""
    try:
        # Test database connectivity
        product_count = db.query(ProductConfiguration).count()
        variant_count = db.query(ConfigurationVariant).count()

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database_connection": "ok",
            "product_configurations_count": product_count,
            "configuration_variants_count": variant_count,
            "service": "product-configurations"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service health check failed: {str(e)}"
        )