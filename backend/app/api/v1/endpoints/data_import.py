from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks, Query
from sqlalchemy.orm import Session
import json
import time
import tempfile
import os
from pathlib import Path

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.scraped_data_processor import scraped_data_processor
from pydantic import BaseModel

router = APIRouter()


class FileImportRequest(BaseModel):
    file_path: str
    override_existing: bool = False
    validate_only: bool = False


class FileImportResponse(BaseModel):
    success: bool
    products_processed: int = 0
    variants_processed: int = 0
    care_packages_created: int = 0
    offers_created: int = 0
    errors: list[str] = []
    warnings: list[str] = []
    processing_time_seconds: float = 0.0
    file_size_mb: Optional[float] = None
    validation_report: Optional[Dict[str, Any]] = None


class DataValidationResponse(BaseModel):
    is_valid: bool
    file_size_mb: float
    structure_valid: bool
    base_product_present: bool
    variants_count: int
    variants_total_declared: int
    data_quality_score: float
    errors: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []


@router.post("/import/file-path", response_model=FileImportResponse)
async def import_from_file_path(
    request: FileImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import scraped product data from a file path on the server"""
    start_time = time.time()

    # Validate file exists
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    if not file_path.suffix.lower() == '.json':
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        # Get file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)

        # Validate file size (max 100MB for safety)
        if file_size_mb > 100:
            raise HTTPException(status_code=413, detail=f"File too large: {file_size_mb:.1f}MB (max 100MB)")

        # Validate JSON structure first if requested
        validation_report = None
        if request.validate_only:
            validation_report = await validate_scraped_data_file(request.file_path)
            return FileImportResponse(
                success=validation_report["is_valid"],
                file_size_mb=file_size_mb,
                processing_time_seconds=time.time() - start_time,
                validation_report=validation_report
            )

        # Process the file
        result = scraped_data_processor.process_scraped_file(request.file_path)

        # Add metadata
        result["file_size_mb"] = file_size_mb
        result["processing_time_seconds"] = time.time() - start_time

        return FileImportResponse(**result)

    except Exception as e:
        return FileImportResponse(
            success=False,
            errors=[f"Import failed: {str(e)}"],
            processing_time_seconds=time.time() - start_time
        )


@router.post("/import/upload", response_model=FileImportResponse)
async def import_from_uploaded_file(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    override_existing: bool = Query(False, description="Override existing products"),
    validate_only: bool = Query(False, description="Only validate, don't import")
):
    """Import scraped product data from an uploaded file"""
    start_time = time.time()

    # Validate file type
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        # Read file content
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)

        # Validate file size
        if file_size_mb > 100:
            raise HTTPException(status_code=413, detail=f"File too large: {file_size_mb:.1f}MB (max 100MB)")

        # Parse JSON
        try:
            json_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

        # Validate structure if requested
        if validate_only:
            validation_report = validate_scraped_data_structure(json_data)
            return FileImportResponse(
                success=validation_report["is_valid"],
                file_size_mb=file_size_mb,
                processing_time_seconds=time.time() - start_time,
                validation_report=validation_report
            )

        # Save to temporary file and process
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(json_data, temp_file, indent=2)
            temp_path = temp_file.name

        try:
            # Process the data
            result = scraped_data_processor.process_scraped_file(temp_path)
            result["file_size_mb"] = file_size_mb
            result["processing_time_seconds"] = time.time() - start_time

            return FileImportResponse(**result)

        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    except Exception as e:
        return FileImportResponse(
            success=False,
            errors=[f"Upload processing failed: {str(e)}"],
            processing_time_seconds=time.time() - start_time
        )


@router.post("/validate/file-path", response_model=DataValidationResponse)
async def validate_file_path(
    file_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate scraped data file structure without importing"""
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    validation_result = await validate_scraped_data_file(file_path)
    return DataValidationResponse(**validation_result)


@router.post("/validate/upload", response_model=DataValidationResponse)
async def validate_uploaded_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate uploaded scraped data file structure"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")

    try:
        content = await file.read()
        json_data = json.loads(content.decode('utf-8'))

        validation_result = validate_scraped_data_structure(json_data)
        validation_result["file_size_mb"] = len(content) / (1024 * 1024)

        return DataValidationResponse(**validation_result)

    except json.JSONDecodeError as e:
        return DataValidationResponse(
            is_valid=False,
            file_size_mb=0,
            structure_valid=False,
            base_product_present=False,
            variants_count=0,
            variants_total_declared=0,
            data_quality_score=0.0,
            errors=[f"Invalid JSON: {str(e)}"]
        )


async def validate_scraped_data_file(file_path: str) -> Dict[str, Any]:
    """Validate scraped data file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return validate_scraped_data_structure(data)
    except Exception as e:
        return {
            "is_valid": False,
            "structure_valid": False,
            "base_product_present": False,
            "variants_count": 0,
            "variants_total_declared": 0,
            "data_quality_score": 0.0,
            "errors": [f"File validation error: {str(e)}"],
            "warnings": [],
            "recommendations": []
        }


def validate_scraped_data_structure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the structure of scraped product data"""
    validation = {
        "is_valid": True,
        "structure_valid": True,
        "base_product_present": False,
        "variants_count": 0,
        "variants_total_declared": 0,
        "data_quality_score": 0.0,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }

    try:
        # Check required top-level keys
        required_keys = ["Base_Product", "Variants_Total", "Variants", "collected_at"]
        missing_keys = [key for key in required_keys if key not in data]

        if missing_keys:
            validation["is_valid"] = False
            validation["structure_valid"] = False
            validation["errors"].append(f"Missing required keys: {missing_keys}")

        # Validate Base_Product
        base_product = data.get("Base_Product", {})
        validation["base_product_present"] = bool(base_product)

        if base_product:
            # Check base product structure
            base_required = ["url", "pdp_summary", "hero_snapshot", "tech_specs"]
            base_missing = [key for key in base_required if key not in base_product]
            if base_missing:
                validation["warnings"].append(f"Base_Product missing recommended keys: {base_missing}")

            # Check if pdp_summary has pricing
            pdp_summary = base_product.get("pdp_summary", {})
            if not pdp_summary.get("sale_price"):
                validation["warnings"].append("Base product missing pricing information")

        # Validate Variants
        variants = data.get("Variants", [])
        variants_total = data.get("Variants_Total", 0)

        validation["variants_count"] = len(variants)
        validation["variants_total_declared"] = variants_total

        if len(variants) != variants_total:
            validation["warnings"].append(
                f"Variants count mismatch: declared {variants_total}, found {len(variants)}"
            )

        # Check variant structure quality
        if variants:
            sample_variant = variants[0]
            variant_required = ["variant_id", "url", "pdp_summary", "tech_specs"]
            variant_missing = [key for key in variant_required if key not in sample_variant]
            if variant_missing:
                validation["warnings"].append(f"Variants missing keys: {variant_missing}")

            # Check pricing data quality
            variants_with_pricing = sum(1 for v in variants if v.get("pdp_summary", {}).get("sale_price"))
            pricing_rate = variants_with_pricing / len(variants) if variants else 0

            # Check tech specs quality
            variants_with_processor = sum(1 for v in variants if v.get("tech_specs", {}).get("Processor"))
            processor_rate = variants_with_processor / len(variants) if variants else 0

            # Calculate data quality score
            quality_factors = [
                pricing_rate,
                processor_rate,
                1.0 if validation["base_product_present"] else 0.0,
                1.0 if abs(len(variants) - variants_total) <= 1 else 0.5,  # Allow 1 variant difference
                1.0 if data.get("collected_at") else 0.0
            ]
            validation["data_quality_score"] = sum(quality_factors) / len(quality_factors)

            # Add recommendations based on quality
            if pricing_rate < 0.9:
                validation["recommendations"].append("Consider improving price data extraction")
            if processor_rate < 0.8:
                validation["recommendations"].append("Consider improving technical specifications extraction")
            if validation["data_quality_score"] < 0.7:
                validation["recommendations"].append("Overall data quality is low - review scraping process")

        # Final validation
        if validation["data_quality_score"] < 0.5:
            validation["is_valid"] = False
            validation["errors"].append("Data quality score too low for reliable import")

        # Check collected_at timestamp
        if not data.get("collected_at"):
            validation["warnings"].append("Missing collection timestamp")

    except Exception as e:
        validation["is_valid"] = False
        validation["structure_valid"] = False
        validation["errors"].append(f"Validation error: {str(e)}")

    return validation


@router.get("/import/status")
async def get_import_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current import/processing status"""
    from app.models.enhanced_product import EnhancedProduct, EnhancedVariant

    try:
        # Get counts
        total_products = db.query(EnhancedProduct).count()
        total_variants = db.query(EnhancedVariant).count()

        # Get recent products
        recent_products = db.query(EnhancedProduct).order_by(
            EnhancedProduct.created_at.desc()
        ).limit(5).all()

        return {
            "status": "operational",
            "statistics": {
                "total_products": total_products,
                "total_variants": total_variants,
                "average_variants_per_product": round(total_variants / total_products, 1) if total_products > 0 else 0
            },
            "recent_imports": [
                {
                    "id": str(product.id),
                    "brand": product.brand,
                    "model": product.model_series,
                    "title": product.full_title,
                    "variants_count": product.variants_count,
                    "imported_at": product.created_at.isoformat()
                }
                for product in recent_products
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting import status: {str(e)}")


@router.delete("/import/cleanup")
async def cleanup_import_data(
    confirm: bool = Query(False, description="Confirm deletion"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clean up all imported data (use with caution)"""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must set confirm=true to proceed with data cleanup"
        )

    try:
        from app.models.enhanced_product import (
            EnhancedProduct, EnhancedVariant, EnhancedPriceHistory,
            TechnicalSpecificationIndex, ProductComparisonCache
        )

        # Count records before deletion
        products_count = db.query(EnhancedProduct).count()
        variants_count = db.query(EnhancedVariant).count()

        # Delete all data (cascading will handle related records)
        db.query(ProductComparisonCache).delete()
        db.query(TechnicalSpecificationIndex).delete()
        db.query(EnhancedPriceHistory).delete()
        db.query(EnhancedVariant).delete()
        db.query(EnhancedProduct).delete()

        db.commit()

        return {
            "success": True,
            "message": "All import data cleaned up successfully",
            "deleted": {
                "products": products_count,
                "variants": variants_count
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for data import service"""
    return {
        "status": "healthy",
        "service": "data-import",
        "timestamp": time.time(),
        "supported_formats": ["JSON"],
        "max_file_size_mb": 100
    }