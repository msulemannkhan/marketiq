import re
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProductDataEnhancer:
    """Enhanced data processing for scraped product configurations"""

    @staticmethod
    def parse_price(price_str: Optional[str]) -> Optional[Decimal]:
        """Parse price string into decimal value"""
        if not price_str:
            return None

        try:
            # Remove currency symbols and commas
            clean_price = re.sub(r'[^\d.]', '', price_str)
            return Decimal(clean_price) if clean_price else None
        except Exception:
            logger.warning(f"Could not parse price: {price_str}")
            return None

    @staticmethod
    def extract_processor_details(processor_str: str) -> Dict[str, Any]:
        """Extract structured processor information"""
        details = {
            "model": None,
            "base_speed": None,
            "max_speed": None,
            "cores": None,
            "threads": None,
            "cache": None,
            "family": None
        }

        if not processor_str:
            return details

        try:
            # Extract processor model (Intel Core Ultra 7 155H, etc.)
            model_match = re.search(r'Intel®?\s*Core™?\s*Ultra?\s*\d+\s*\w+', processor_str, re.IGNORECASE)
            if model_match:
                details["model"] = model_match.group().strip()

            # Extract max speed (up to 4.8 GHz)
            speed_match = re.search(r'up to\s+([\d.]+)\s*GHz', processor_str, re.IGNORECASE)
            if speed_match:
                details["max_speed"] = f"{speed_match.group(1)} GHz"

            # Extract cores (16 cores)
            cores_match = re.search(r'(\d+)\s*cores?', processor_str, re.IGNORECASE)
            if cores_match:
                details["cores"] = int(cores_match.group(1))

            # Extract threads (22 threads)
            threads_match = re.search(r'(\d+)\s*threads?', processor_str, re.IGNORECASE)
            if threads_match:
                details["threads"] = int(threads_match.group(1))

            # Extract cache (24 MB L3 cache)
            cache_match = re.search(r'(\d+)\s*MB\s*L\d+\s*cache', processor_str, re.IGNORECASE)
            if cache_match:
                details["cache"] = f"{cache_match.group(1)} MB"

        except Exception as e:
            logger.warning(f"Error parsing processor details: {e}")

        return details

    @staticmethod
    def extract_memory_details(memory_str: str) -> Dict[str, Any]:
        """Extract structured memory information"""
        details = {
            "size_gb": None,
            "type": None,
            "speed": None,
            "configuration": None
        }

        if not memory_str:
            return details

        try:
            # Extract size (32 GB, 16 GB)
            size_match = re.search(r'(\d+)\s*GB', memory_str, re.IGNORECASE)
            if size_match:
                details["size_gb"] = int(size_match.group(1))

            # Extract type (DDR5)
            type_match = re.search(r'(DDR\d+)', memory_str, re.IGNORECASE)
            if type_match:
                details["type"] = type_match.group(1)

            # Extract speed (5600 MT/s)
            speed_match = re.search(r'(\d+)\s*MT/s', memory_str, re.IGNORECASE)
            if speed_match:
                details["speed"] = f"{speed_match.group(1)} MT/s"

            # Extract configuration (2 x 16 GB)
            config_match = re.search(r'\(([^)]+)\)', memory_str)
            if config_match:
                details["configuration"] = config_match.group(1)

        except Exception as e:
            logger.warning(f"Error parsing memory details: {e}")

        return details

    @staticmethod
    def extract_storage_details(storage_str: str) -> Dict[str, Any]:
        """Extract structured storage information"""
        details = {
            "size_gb": None,
            "type": None,
            "interface": None
        }

        if not storage_str:
            return details

        try:
            # Extract size (1 TB = 1000 GB, 512 GB)
            if "TB" in storage_str:
                tb_match = re.search(r'(\d+)\s*TB', storage_str, re.IGNORECASE)
                if tb_match:
                    details["size_gb"] = int(tb_match.group(1)) * 1000
            else:
                gb_match = re.search(r'(\d+)\s*GB', storage_str, re.IGNORECASE)
                if gb_match:
                    details["size_gb"] = int(gb_match.group(1))

            # Extract type (SSD, HDD)
            if "SSD" in storage_str.upper():
                details["type"] = "SSD"
            elif "HDD" in storage_str.upper():
                details["type"] = "HDD"

            # Extract interface (PCIe NVMe)
            interface_match = re.search(r'(PCIe®?\s*NVMe™?)', storage_str, re.IGNORECASE)
            if interface_match:
                details["interface"] = "PCIe NVMe"

        except Exception as e:
            logger.warning(f"Error parsing storage details: {e}")

        return details

    @staticmethod
    def extract_display_details(display_str: str) -> Dict[str, Any]:
        """Extract structured display information"""
        details = {
            "size_inches": None,
            "resolution": None,
            "resolution_standard": None,
            "touch": None,
            "panel_type": None,
            "brightness_nits": None,
            "color_gamut": None
        }

        if not display_str:
            return details

        try:
            # Extract size (16", 14")
            size_match = re.search(r'(\d+)"', display_str)
            if size_match:
                details["size_inches"] = int(size_match.group(1))

            # Extract resolution (1920 x 1200)
            res_match = re.search(r'(\d+)\s*x\s*(\d+)', display_str)
            if res_match:
                details["resolution"] = f"{res_match.group(1)}x{res_match.group(2)}"

            # Extract resolution standard (WUXGA)
            if "WUXGA" in display_str:
                details["resolution_standard"] = "WUXGA"
            elif "FHD" in display_str or "Full HD" in display_str:
                details["resolution_standard"] = "FHD"

            # Check for touch
            details["touch"] = "touch" in display_str.lower()

            # Extract panel type (IPS)
            if "IPS" in display_str.upper():
                details["panel_type"] = "IPS"

            # Extract brightness (300 nits)
            brightness_match = re.search(r'(\d+)\s*nits', display_str, re.IGNORECASE)
            if brightness_match:
                details["brightness_nits"] = int(brightness_match.group(1))

            # Extract color gamut (45% NTSC)
            color_match = re.search(r'(\d+)%\s*NTSC', display_str, re.IGNORECASE)
            if color_match:
                details["color_gamut"] = f"{color_match.group(1)}% NTSC"

        except Exception as e:
            logger.warning(f"Error parsing display details: {e}")

        return details

    @staticmethod
    def extract_dimensions_weight(dimensions_str: str, weight_str: str) -> Dict[str, Any]:
        """Extract structured physical dimensions"""
        details = {
            "width_inches": None,
            "depth_inches": None,
            "height_front_inches": None,
            "height_rear_inches": None,
            "weight_lbs": None
        }

        try:
            # Extract dimensions (14.15 x 9.88 x 0.43 in (front); 14.15 x 9.88 x 0.67 in (rear))
            if dimensions_str:
                dims_match = re.search(r'([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)', dimensions_str)
                if dims_match:
                    details["width_inches"] = float(dims_match.group(1))
                    details["depth_inches"] = float(dims_match.group(2))
                    details["height_front_inches"] = float(dims_match.group(3))

                # Check for rear height
                rear_match = re.search(r'([\d.]+)\s*in\s*\(rear\)', dimensions_str)
                if rear_match:
                    details["height_rear_inches"] = float(rear_match.group(1))

            # Extract weight (Starting at 3.85 lb)
            if weight_str:
                weight_match = re.search(r'([\d.]+)\s*lb', weight_str, re.IGNORECASE)
                if weight_match:
                    details["weight_lbs"] = float(weight_match.group(1))

        except Exception as e:
            logger.warning(f"Error parsing dimensions/weight: {e}")

        return details

    @classmethod
    def enhance_variant_data(cls, variant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a single variant with structured data"""
        enhanced = variant_data.copy()

        # Extract pricing
        pdp_summary = variant_data.get("pdp_summary", {})
        enhanced["pricing"] = {
            "list_price_decimal": cls.parse_price(pdp_summary.get("list_price")),
            "sale_price_decimal": cls.parse_price(pdp_summary.get("sale_price")),
            "savings_decimal": cls.parse_price(pdp_summary.get("save_text")),
            "discount_percentage": int(re.sub(r'[^\d]', '', pdp_summary.get("discount_label", "0")) or 0),
        }

        # Extract structured tech specs
        tech_specs = variant_data.get("tech_specs", {})
        enhanced["structured_specs"] = {
            "processor": cls.extract_processor_details(tech_specs.get("Processor", "")),
            "memory": cls.extract_memory_details(tech_specs.get("Memory", "")),
            "storage": cls.extract_storage_details(tech_specs.get("Internal drive", "")),
            "display": cls.extract_display_details(tech_specs.get("Display", "")),
            "physical": cls.extract_dimensions_weight(
                tech_specs.get("Dimensions (W X D X H)", ""),
                tech_specs.get("Weight", "")
            ),
        }

        return enhanced

    @classmethod
    def enhance_product_configuration(cls, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance entire product configuration data"""
        enhanced = json_data.copy()

        # Enhance base product
        base_product = enhanced.get("Base_Product", {})
        if base_product:
            enhanced["Base_Product"] = cls.enhance_variant_data(base_product)

        # Enhance all variants
        variants = enhanced.get("Variants", [])
        enhanced["Variants"] = [
            cls.enhance_variant_data(variant) for variant in variants
        ]

        # Add metadata
        enhanced["enhancement_metadata"] = {
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": "1.0",
            "total_variants": len(variants)
        }

        return enhanced

    @staticmethod
    def validate_enhanced_data(enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate enhanced data quality"""
        validation_report = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "statistics": {}
        }

        try:
            variants = enhanced_data.get("Variants", [])

            # Count variants with parsed pricing
            valid_prices = sum(1 for v in variants if v.get("pricing", {}).get("sale_price_decimal"))

            # Count variants with structured specs
            valid_processors = sum(1 for v in variants if v.get("structured_specs", {}).get("processor", {}).get("model"))

            validation_report["statistics"] = {
                "total_variants": len(variants),
                "variants_with_valid_pricing": valid_prices,
                "variants_with_processor_details": valid_processors,
                "pricing_parse_rate": round(valid_prices / len(variants) * 100, 1) if variants else 0,
                "processor_parse_rate": round(valid_processors / len(variants) * 100, 1) if variants else 0
            }

            # Add warnings for low parse rates
            if validation_report["statistics"]["pricing_parse_rate"] < 90:
                validation_report["warnings"].append("Low pricing data parse rate")

            if validation_report["statistics"]["processor_parse_rate"] < 80:
                validation_report["warnings"].append("Low processor details parse rate")

        except Exception as e:
            validation_report["is_valid"] = False
            validation_report["errors"].append(f"Validation error: {str(e)}")

        return validation_report


# Convenience functions
def enhance_product_data(json_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Enhance product data and return enhanced data + validation report"""
    enhanced_data = ProductDataEnhancer.enhance_product_configuration(json_data)
    validation_report = ProductDataEnhancer.validate_enhanced_data(enhanced_data)
    return enhanced_data, validation_report