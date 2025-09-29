import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.crud.product_config import BulkProductConfigCRUD
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class ProductConfigurationImportService:
    """Service for importing product configuration data from JSON files"""

    def __init__(self):
        self.logger = logger

    async def import_from_file(
        self,
        file_path: str,
        override_existing: bool = False
    ) -> Dict[str, Any]:
        """Import product configurations from a JSON file"""
        try:
            # Validate file exists
            path = Path(file_path)
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            # Read and parse JSON
            with open(path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            return await self.import_from_json(json_data, override_existing)

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON file: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Import error: {e}")
            return {
                "success": False,
                "error": f"Import failed: {str(e)}"
            }

    async def import_from_json(
        self,
        json_data: Dict[str, Any],
        override_existing: bool = False
    ) -> Dict[str, Any]:
        """Import product configurations from JSON data"""
        db = SessionLocal()
        try:
            result = BulkProductConfigCRUD.import_from_json(
                db=db,
                json_data=json_data,
                override_existing=override_existing
            )

            self.logger.info(f"Import completed: {result}")
            return result

        except Exception as e:
            self.logger.error(f"Database import error: {e}")
            return {
                "success": False,
                "error": f"Database import failed: {str(e)}"
            }
        finally:
            db.close()

    async def validate_json_structure(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure of product configuration JSON"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }

        try:
            # Check required top-level keys
            required_keys = ["Base_Product", "Variants_Total", "Variants", "collected_at"]
            missing_keys = [key for key in required_keys if key not in json_data]

            if missing_keys:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Missing required keys: {missing_keys}")

            # Validate Base_Product structure
            base_product = json_data.get("Base_Product", {})
            if base_product:
                base_required = ["url", "pdp_summary", "hero_snapshot", "tech_specs"]
                base_missing = [key for key in base_required if key not in base_product]
                if base_missing:
                    validation_result["warnings"].append(f"Base_Product missing recommended keys: {base_missing}")

            # Validate Variants structure
            variants = json_data.get("Variants", [])
            variants_total = json_data.get("Variants_Total", 0)

            if len(variants) != variants_total:
                validation_result["warnings"].append(
                    f"Variants count mismatch: expected {variants_total}, found {len(variants)}"
                )

            # Check variant structure
            if variants:
                sample_variant = variants[0]
                variant_required = ["variant_id", "url", "pdp_summary", "tech_specs"]
                variant_missing = [key for key in variant_required if key not in sample_variant]
                if variant_missing:
                    validation_result["warnings"].append(f"Variants missing recommended keys: {variant_missing}")

            # Generate summary
            validation_result["summary"] = {
                "has_base_product": bool(base_product),
                "variants_count": len(variants),
                "variants_total_declared": variants_total,
                "has_collected_timestamp": bool(json_data.get("collected_at")),
                "estimated_size_mb": len(json.dumps(json_data).encode('utf-8')) / (1024 * 1024)
            }

        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")

        return validation_result

    async def extract_product_info(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key product information from JSON data"""
        try:
            base_product = json_data.get("Base_Product", {})
            variants = json_data.get("Variants", [])

            # Extract base product info
            pdp_summary = base_product.get("pdp_summary", {})
            title = pdp_summary.get("title", "")

            # Determine brand and model
            brand = "Unknown"
            model_family = "Unknown"

            if "HP" in title:
                brand = "HP"
                if "ProBook" in title:
                    if "460" in title:
                        model_family = "ProBook 460"
                    elif "440" in title:
                        model_family = "ProBook 440"
                    else:
                        model_family = "ProBook"
            elif "Lenovo" in title or "ThinkPad" in title:
                brand = "Lenovo"
                if "ThinkPad" in title:
                    model_family = "ThinkPad E14"

            # Extract price range from variants
            prices = []
            for variant in variants:
                variant_pdp = variant.get("pdp_summary", {})
                sale_price_str = variant_pdp.get("sale_price", "0").replace("$", "").replace(",", "")
                try:
                    price = float(sale_price_str)
                    if price > 0:
                        prices.append(price)
                except (ValueError, TypeError):
                    continue

            # Extract unique processors
            processors = set()
            for variant in variants:
                tech_specs = variant.get("tech_specs", {})
                processor = tech_specs.get("Processor family", "")
                if processor:
                    processors.add(processor)

            # Extract unique memory options
            memory_options = set()
            for variant in variants:
                tech_specs = variant.get("tech_specs", {})
                memory = tech_specs.get("Memory", "")
                if memory:
                    memory_options.add(memory)

            return {
                "brand": brand,
                "model_family": model_family,
                "title": title,
                "base_url": base_product.get("url", ""),
                "variants_count": len(variants),
                "price_range": {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                    "average": sum(prices) / len(prices) if prices else 0
                },
                "unique_processors": list(processors),
                "unique_memory_options": list(memory_options),
                "collected_at": json_data.get("collected_at")
            }

        except Exception as e:
            logger.error(f"Error extracting product info: {e}")
            return {"error": str(e)}

    async def batch_import_multiple_files(
        self,
        file_paths: List[str],
        override_existing: bool = False
    ) -> Dict[str, Any]:
        """Import multiple product configuration files in batch"""
        results = {
            "total_files": len(file_paths),
            "successful_imports": 0,
            "failed_imports": 0,
            "results": [],
            "summary": {
                "total_products_created": 0,
                "total_variants_created": 0,
                "total_errors": []
            }
        }

        for file_path in file_paths:
            try:
                result = await self.import_from_file(file_path, override_existing)

                if result.get("success"):
                    results["successful_imports"] += 1
                    results["summary"]["total_products_created"] += result.get("products_created", 0)
                    results["summary"]["total_variants_created"] += result.get("variants_created", 0)
                else:
                    results["failed_imports"] += 1
                    results["summary"]["total_errors"].extend(result.get("errors", []))

                results["results"].append({
                    "file_path": file_path,
                    "result": result
                })

            except Exception as e:
                results["failed_imports"] += 1
                error_msg = f"Failed to process {file_path}: {str(e)}"
                results["summary"]["total_errors"].append(error_msg)
                results["results"].append({
                    "file_path": file_path,
                    "result": {"success": False, "error": error_msg}
                })

        return results

    async def get_import_recommendations(self, json_data: Dict[str, Any]) -> List[str]:
        """Get recommendations for importing the JSON data"""
        recommendations = []

        try:
            # Check data size
            data_size_mb = len(json.dumps(json_data).encode('utf-8')) / (1024 * 1024)
            if data_size_mb > 50:
                recommendations.append("Large file detected (>50MB). Consider processing in smaller batches.")

            # Check variants count
            variants_count = len(json_data.get("Variants", []))
            if variants_count > 100:
                recommendations.append("High variant count detected. Import may take several minutes.")

            # Check for existing data
            base_url = json_data.get("Base_Product", {}).get("url", "")
            if base_url:
                db = SessionLocal()
                try:
                    from app.crud.product_config import ProductConfigurationCRUD
                    existing = ProductConfigurationCRUD.get_by_url(db, base_url)
                    if existing:
                        recommendations.append("Product configuration already exists. Use override_existing=true to update.")
                finally:
                    db.close()

            # Check data freshness
            collected_at_str = json_data.get("collected_at")
            if collected_at_str:
                try:
                    collected_at = datetime.fromisoformat(collected_at_str.replace("Z", "+00:00"))
                    hours_old = (datetime.utcnow() - collected_at).total_seconds() / 3600
                    if hours_old > 24:
                        recommendations.append(f"Data is {hours_old:.1f} hours old. Consider refreshing.")
                except:
                    pass

            # Check for missing price data
            variants = json_data.get("Variants", [])
            variants_without_price = 0
            for variant in variants:
                sale_price = variant.get("pdp_summary", {}).get("sale_price")
                if not sale_price or sale_price == "$0.00":
                    variants_without_price += 1

            if variants_without_price > 0:
                recommendations.append(f"{variants_without_price} variants have missing or zero prices.")

        except Exception as e:
            recommendations.append(f"Error analyzing data: {str(e)}")

        return recommendations


# Global instance
product_config_import_service = ProductConfigurationImportService()


# Convenience functions
async def import_product_configurations_from_file(
    file_path: str,
    override_existing: bool = False
) -> Dict[str, Any]:
    """Convenience function to import from file"""
    return await product_config_import_service.import_from_file(file_path, override_existing)


async def validate_product_configuration_json(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate JSON"""
    return await product_config_import_service.validate_json_structure(json_data)


async def get_product_configuration_info(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to extract product info"""
    return await product_config_import_service.extract_product_info(json_data)