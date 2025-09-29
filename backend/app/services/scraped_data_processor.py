import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.enhanced_product import (
    EnhancedProduct, EnhancedVariant, EnhancedPriceHistory,
    TechnicalSpecificationIndex, ProductComparisonCache,
    EnhancedCarePackage, EnhancedProductOffer
)
from app.models.product_config import VariantOffer
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class ScrapedDataProcessor:
    """Process HP scraped data format into optimized database structure"""

    def __init__(self):
        self.logger = logger

    @staticmethod
    def clean_price_string(price_str: Optional[str]) -> Optional[Decimal]:
        """Convert price string to decimal: '$3,489.00' -> 3489.00"""
        if not price_str:
            return None

        try:
            # Remove everything except digits, dots, and commas
            clean_str = re.sub(r'[^\d.,]', '', price_str)
            # Remove commas
            clean_str = clean_str.replace(',', '')
            return Decimal(clean_str) if clean_str else None
        except (InvalidOperation, ValueError):
            logger.warning(f"Could not parse price: {price_str}")
            return None

    @staticmethod
    def extract_processor_specs(processor_text: str) -> Dict[str, Any]:
        """Extract structured processor data from text"""
        specs = {
            "brand": None,
            "family": None,
            "model": None,
            "base_speed_ghz": None,
            "max_speed_ghz": None,
            "cores": None,
            "threads": None,
            "cache_mb": None,
            "architecture": None
        }

        if not processor_text:
            return specs

        try:
            # Brand extraction
            if "Intel" in processor_text:
                specs["brand"] = "Intel"
            elif "AMD" in processor_text:
                specs["brand"] = "AMD"

            # Family extraction (Intel Core Ultra 7, Core i7, etc.)
            family_patterns = [
                r'Intel®?\s*Core™?\s*Ultra?\s*\d+',
                r'Intel®?\s*Core™?\s*i\d+',
                r'AMD\s*Ryzen™?\s*\d+',
            ]
            for pattern in family_patterns:
                match = re.search(pattern, processor_text, re.IGNORECASE)
                if match:
                    specs["family"] = match.group().strip()
                    break

            # Model extraction (155H, 7840U, etc.)
            model_match = re.search(r'([A-Z]?\d+[A-Z]+)', processor_text)
            if model_match:
                specs["model"] = model_match.group(1)

            # Speed extraction
            speed_match = re.search(r'up to\s+([\d.]+)\s*GHz', processor_text, re.IGNORECASE)
            if speed_match:
                specs["max_speed_ghz"] = float(speed_match.group(1))

            # Base speed (less common but sometimes present)
            base_speed_match = re.search(r'([\d.]+)\s*GHz\s*base', processor_text, re.IGNORECASE)
            if base_speed_match:
                specs["base_speed_ghz"] = float(base_speed_match.group(1))

            # Cores extraction
            cores_match = re.search(r'(\d+)\s*cores?', processor_text, re.IGNORECASE)
            if cores_match:
                specs["cores"] = int(cores_match.group(1))

            # Threads extraction
            threads_match = re.search(r'(\d+)\s*threads?', processor_text, re.IGNORECASE)
            if threads_match:
                specs["threads"] = int(threads_match.group(1))

            # Cache extraction
            cache_match = re.search(r'(\d+)\s*MB\s*L\d+\s*cache', processor_text, re.IGNORECASE)
            if cache_match:
                specs["cache_mb"] = int(cache_match.group(1))

        except Exception as e:
            logger.warning(f"Error parsing processor specs: {e}")

        return specs

    @staticmethod
    def extract_memory_specs(memory_text: str) -> Dict[str, Any]:
        """Extract structured memory data"""
        specs = {
            "size_gb": None,
            "type": None,
            "speed_mts": None,
            "slots_total": None,
            "configuration": None
        }

        if not memory_text:
            return specs

        try:
            # Size extraction (32 GB, 16 GB)
            size_match = re.search(r'(\d+)\s*GB', memory_text, re.IGNORECASE)
            if size_match:
                specs["size_gb"] = int(size_match.group(1))

            # Type extraction (DDR5, DDR4)
            type_match = re.search(r'(DDR\d+)', memory_text, re.IGNORECASE)
            if type_match:
                specs["type"] = type_match.group(1).upper()

            # Speed extraction (5600 MT/s)
            speed_match = re.search(r'(\d+)\s*MT/s', memory_text, re.IGNORECASE)
            if speed_match:
                specs["speed_mts"] = int(speed_match.group(1))

            # Configuration extraction (2 x 16 GB)
            config_match = re.search(r'\(([^)]+)\)', memory_text)
            if config_match:
                specs["configuration"] = config_match.group(1)

            # Slots extraction (2 SODIMM)
            slots_text = memory_text  # This would come from memory slots field
            slots_match = re.search(r'(\d+)\s*SODIMM', slots_text, re.IGNORECASE)
            if slots_match:
                specs["slots_total"] = int(slots_match.group(1))

        except Exception as e:
            logger.warning(f"Error parsing memory specs: {e}")

        return specs

    @staticmethod
    def extract_storage_specs(storage_text: str) -> Dict[str, Any]:
        """Extract structured storage data"""
        specs = {
            "size_gb": None,
            "type": None,
            "interface": None,
            "form_factor": None
        }

        if not storage_text:
            return specs

        try:
            # Size extraction
            if "TB" in storage_text.upper():
                tb_match = re.search(r'(\d+)\s*TB', storage_text, re.IGNORECASE)
                if tb_match:
                    specs["size_gb"] = int(tb_match.group(1)) * 1000
            else:
                gb_match = re.search(r'(\d+)\s*GB', storage_text, re.IGNORECASE)
                if gb_match:
                    specs["size_gb"] = int(gb_match.group(1))

            # Type extraction
            if "SSD" in storage_text.upper():
                specs["type"] = "SSD"
            elif "HDD" in storage_text.upper():
                specs["type"] = "HDD"

            # Interface extraction
            if "PCIe" in storage_text and "NVMe" in storage_text:
                specs["interface"] = "PCIe NVMe"
            elif "SATA" in storage_text.upper():
                specs["interface"] = "SATA"

            # Form factor (usually M.2 for modern SSDs)
            if "M.2" in storage_text:
                specs["form_factor"] = "M.2"

        except Exception as e:
            logger.warning(f"Error parsing storage specs: {e}")

        return specs

    @staticmethod
    def extract_display_specs(display_text: str) -> Dict[str, Any]:
        """Extract structured display data"""
        specs = {
            "size_inches": None,
            "resolution": None,
            "resolution_standard": None,
            "touch": False,
            "panel_type": None,
            "brightness_nits": None,
            "color_gamut_percent": None,
            "color_gamut_standard": None
        }

        if not display_text:
            return specs

        try:
            # Size extraction (16", 14")
            size_match = re.search(r'(\d+)"', display_text)
            if size_match:
                specs["size_inches"] = int(size_match.group(1))

            # Resolution extraction (1920 x 1200)
            resolution_match = re.search(r'(\d+)\s*x\s*(\d+)', display_text)
            if resolution_match:
                specs["resolution"] = f"{resolution_match.group(1)}x{resolution_match.group(2)}"

            # Resolution standard (WUXGA, FHD)
            if "WUXGA" in display_text.upper():
                specs["resolution_standard"] = "WUXGA"
            elif "FHD" in display_text.upper() or "Full HD" in display_text:
                specs["resolution_standard"] = "FHD"
            elif "4K" in display_text.upper():
                specs["resolution_standard"] = "4K"

            # Touch capability
            specs["touch"] = "touch" in display_text.lower()

            # Panel type
            if "IPS" in display_text.upper():
                specs["panel_type"] = "IPS"
            elif "OLED" in display_text.upper():
                specs["panel_type"] = "OLED"
            elif "VA" in display_text.upper():
                specs["panel_type"] = "VA"

            # Brightness (300 nits)
            brightness_match = re.search(r'(\d+)\s*nits?', display_text, re.IGNORECASE)
            if brightness_match:
                specs["brightness_nits"] = int(brightness_match.group(1))

            # Color gamut (45% NTSC)
            color_match = re.search(r'(\d+)%\s*(NTSC|sRGB|Adobe RGB)', display_text, re.IGNORECASE)
            if color_match:
                specs["color_gamut_percent"] = int(color_match.group(1))
                specs["color_gamut_standard"] = color_match.group(2).upper()

        except Exception as e:
            logger.warning(f"Error parsing display specs: {e}")

        return specs

    @staticmethod
    def extract_physical_specs(dimensions_text: str, weight_text: str) -> Dict[str, Any]:
        """Extract physical dimensions and weight"""
        specs = {
            "width_inches": None,
            "depth_inches": None,
            "height_front_inches": None,
            "height_rear_inches": None,
            "weight_lbs": None
        }

        try:
            # Dimensions (14.15 x 9.88 x 0.43 in)
            if dimensions_text:
                dims_match = re.search(r'([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)', dimensions_text)
                if dims_match:
                    specs["width_inches"] = float(dims_match.group(1))
                    specs["depth_inches"] = float(dims_match.group(2))
                    specs["height_front_inches"] = float(dims_match.group(3))

                # Check for rear height
                rear_match = re.search(r'([\d.]+)\s*in\s*\(rear\)', dimensions_text)
                if rear_match:
                    specs["height_rear_inches"] = float(rear_match.group(1))

            # Weight (Starting at 3.85 lb)
            if weight_text:
                weight_match = re.search(r'([\d.]+)\s*lb', weight_text, re.IGNORECASE)
                if weight_match:
                    specs["weight_lbs"] = float(weight_match.group(1))

        except Exception as e:
            logger.warning(f"Error parsing physical specs: {e}")

        return specs

    @staticmethod
    def extract_connectivity_specs(tech_specs: Dict[str, str]) -> Dict[str, Any]:
        """Extract connectivity information"""
        specs = {
            "usb_c_ports": 0,
            "usb_a_ports": 0,
            "hdmi_ports": 0,
            "ethernet_port": False,
            "audio_jack": False,
            "wifi_standard": None,
            "bluetooth_version": None
        }

        try:
            # USB and port extraction
            ports_text = tech_specs.get("External I/O Ports", "")
            if ports_text:
                # USB-C ports
                usb_c_match = re.search(r'(\d+)\s*USB\s*Type-C', ports_text, re.IGNORECASE)
                if usb_c_match:
                    specs["usb_c_ports"] = int(usb_c_match.group(1))

                # USB-A ports
                usb_a_match = re.search(r'(\d+)\s*USB\s*Type-A', ports_text, re.IGNORECASE)
                if usb_a_match:
                    specs["usb_a_ports"] = int(usb_a_match.group(1))

                # HDMI
                specs["hdmi_ports"] = 1 if "HDMI" in ports_text else 0

                # Ethernet
                specs["ethernet_port"] = "RJ-45" in ports_text

                # Audio jack
                specs["audio_jack"] = "headphone" in ports_text.lower() or "audio" in ports_text.lower()

            # Wireless technology
            wireless_text = tech_specs.get("Wireless technology", "")
            if wireless_text:
                # WiFi standard
                wifi_match = re.search(r'Wi-Fi\s*(\w+)', wireless_text, re.IGNORECASE)
                if wifi_match:
                    specs["wifi_standard"] = f"Wi-Fi {wifi_match.group(1)}"

                # Bluetooth
                bluetooth_match = re.search(r'Bluetooth®?\s*([\d.]+)', wireless_text, re.IGNORECASE)
                if bluetooth_match:
                    specs["bluetooth_version"] = bluetooth_match.group(1)

        except Exception as e:
            logger.warning(f"Error parsing connectivity specs: {e}")

        return specs

    def process_scraped_file(self, file_path: str) -> Dict[str, Any]:
        """Process entire scraped JSON file"""
        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            return self.process_scraped_data(data)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "products_processed": 0,
                "variants_processed": 0
            }

    def process_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process scraped data structure into database"""
        result = {
            "success": False,
            "products_processed": 0,
            "variants_processed": 0,
            "care_packages_created": 0,
            "offers_created": 0,
            "errors": [],
            "warnings": []
        }

        db = SessionLocal()
        try:
            # Extract base product information
            base_product = data.get("Base_Product", {})
            if not base_product:
                result["errors"].append("No Base_Product found in data")
                return result

            # Parse collection timestamp
            collected_at_str = data.get("collected_at")
            collected_at = datetime.fromisoformat(collected_at_str.replace("Z", "+00:00")) if collected_at_str else datetime.utcnow()

            # Extract product family information
            product_info = self._extract_product_family_info(base_product)

            # Check if product already exists
            existing_product = db.query(EnhancedProduct).filter(
                EnhancedProduct.product_url == base_product.get("url", "")
            ).first()

            if existing_product:
                result["warnings"].append(f"Product already exists: {existing_product.full_title}")
                # Update existing product
                product = self._update_existing_product(db, existing_product, base_product, collected_at)
            else:
                # Create new product
                product = self._create_new_product(db, base_product, product_info, collected_at)
                result["products_processed"] = 1

            # Process care packages (only once per product)
            care_packages = base_product.get("hero_snapshot", {}).get("care_packs", [])
            if care_packages:
                care_count = self._process_care_packages(db, product.id, care_packages)
                result["care_packages_created"] = care_count

            # Process variants
            variants = data.get("Variants", [])
            for variant_data in variants:
                try:
                    variant = self._process_variant(db, product.id, variant_data)
                    if variant:
                        result["variants_processed"] += 1

                        # Process variant offers
                        offers = variant_data.get("hero_snapshot", {}).get("offers", [])
                        if offers:
                            offer_count = self._process_variant_offers(db, variant.id, offers)
                            result["offers_created"] += offer_count

                except Exception as e:
                    result["errors"].append(f"Error processing variant {variant_data.get('variant_id', 'unknown')}: {str(e)}")

            # Update product variant count
            product.variants_count = result["variants_processed"]
            db.commit()

            result["success"] = True

        except Exception as e:
            logger.error(f"Error processing scraped data: {e}")
            result["errors"].append(f"Processing failed: {str(e)}")
            db.rollback()
        finally:
            db.close()

        return result

    def _extract_product_family_info(self, base_product: Dict[str, Any]) -> Dict[str, str]:
        """Extract product family information from base product"""
        pdp_summary = base_product.get("pdp_summary", {})
        title = pdp_summary.get("title", "")

        info = {
            "brand": "Unknown",
            "model_series": "Unknown",
            "model_generation": "Unknown",
            "full_title": title
        }

        try:
            if "HP" in title:
                info["brand"] = "HP"
                if "ProBook" in title:
                    if "460" in title:
                        info["model_series"] = "ProBook 460"
                    elif "440" in title:
                        info["model_series"] = "ProBook 440"
                    else:
                        info["model_series"] = "ProBook"

                    # Extract generation (G11, G10)
                    gen_match = re.search(r'G(\d+)', title)
                    if gen_match:
                        info["model_generation"] = f"G{gen_match.group(1)}"

            elif "Lenovo" in title or "ThinkPad" in title:
                info["brand"] = "Lenovo"
                if "ThinkPad" in title:
                    info["model_series"] = "ThinkPad E14"
                    # Extract generation
                    gen_match = re.search(r'Gen\s*(\d+)', title)
                    if gen_match:
                        info["model_generation"] = f"Gen {gen_match.group(1)}"

        except Exception as e:
            logger.warning(f"Error extracting product family info: {e}")

        return info

    def _create_new_product(self, db: Session, base_product: Dict[str, Any], product_info: Dict[str, str], collected_at: datetime) -> EnhancedProduct:
        """Create new enhanced product"""
        pdp_summary = base_product.get("pdp_summary", {})

        product = EnhancedProduct(
            brand=product_info["brand"],
            model_series=product_info["model_series"],
            model_generation=product_info["model_generation"],
            full_title=product_info["full_title"],
            product_url=base_product.get("url", ""),

            usage_category=pdp_summary.get("usage_label", "").split("|")[1].strip() if "|" in pdp_summary.get("usage_label", "") else None,
            energy_star="ENERGY STAR" in pdp_summary.get("usage_label", ""),
            sustainability_certified=bool(base_product.get("hero_snapshot", {}).get("sustainability_badge")),

            base_sku=pdp_summary.get("sku_hint", ""),
            base_list_price=self.clean_price_string(pdp_summary.get("list_price")),
            base_sale_price=self.clean_price_string(pdp_summary.get("sale_price")),
            base_discount_percentage=int(re.sub(r'[^\d]', '', pdp_summary.get("discount_label", "0")) or 0),

            average_rating=Decimal(pdp_summary.get("rating")) if pdp_summary.get("rating") else None,
            total_reviews=int(pdp_summary.get("review_count")) if pdp_summary.get("review_count") else None,

            scraped_at=collected_at,
            data_version="2.0"
        )

        db.add(product)
        db.flush()  # Get the ID
        return product

    def _update_existing_product(self, db: Session, product: EnhancedProduct, base_product: Dict[str, Any], collected_at: datetime) -> EnhancedProduct:
        """Update existing product with new data"""
        pdp_summary = base_product.get("pdp_summary", {})

        # Update pricing and review data
        product.base_list_price = self.clean_price_string(pdp_summary.get("list_price"))
        product.base_sale_price = self.clean_price_string(pdp_summary.get("sale_price"))
        product.base_discount_percentage = int(re.sub(r'[^\d]', '', pdp_summary.get("discount_label", "0")) or 0)
        product.average_rating = Decimal(pdp_summary.get("rating")) if pdp_summary.get("rating") else None
        product.total_reviews = int(pdp_summary.get("review_count")) if pdp_summary.get("review_count") else None
        product.scraped_at = collected_at

        return product

    def _process_variant(self, db: Session, product_id: str, variant_data: Dict[str, Any]) -> Optional[EnhancedVariant]:
        """Process a single variant"""
        try:
            pdp_summary = variant_data.get("pdp_summary", {})
            tech_specs = variant_data.get("tech_specs", {})

            # Extract all structured specs
            processor_specs = self.extract_processor_specs(tech_specs.get("Processor", ""))
            memory_specs = self.extract_memory_specs(tech_specs.get("Memory", ""))
            storage_specs = self.extract_storage_specs(tech_specs.get("Internal drive", ""))
            display_specs = self.extract_display_specs(tech_specs.get("Display", ""))
            physical_specs = self.extract_physical_specs(
                tech_specs.get("Dimensions (W X D X H)", ""),
                tech_specs.get("Weight", "")
            )
            connectivity_specs = self.extract_connectivity_specs(tech_specs)

            # Parse timestamp
            variant_timestamp = None
            if variant_data.get("timestamp"):
                try:
                    variant_timestamp = datetime.fromisoformat(variant_data["timestamp"].replace("Z", "+00:00"))
                except:
                    pass

            # Create variant
            variant = EnhancedVariant(
                product_id=product_id,
                variant_id=variant_data.get("variant_id", ""),
                sku=pdp_summary.get("sku_hint", ""),
                variant_url=variant_data.get("url", ""),

                # Pricing
                list_price=self.clean_price_string(pdp_summary.get("list_price")),
                sale_price=self.clean_price_string(pdp_summary.get("sale_price")),
                discount_percentage=int(re.sub(r'[^\d]', '', pdp_summary.get("discount_label", "0")) or 0),
                savings_amount=self.clean_price_string(pdp_summary.get("save_text")),

                # Stock
                stock_status=pdp_summary.get("stock", "").lower().replace(" ", "_"),
                estimated_ship_days=self._extract_ship_days(pdp_summary.get("delivery", "")),

                # Processor
                processor_brand=processor_specs["brand"],
                processor_family=processor_specs["family"],
                processor_model=processor_specs["model"],
                processor_base_speed=f"{processor_specs['base_speed_ghz']} GHz" if processor_specs["base_speed_ghz"] else None,
                processor_max_speed=f"{processor_specs['max_speed_ghz']} GHz" if processor_specs["max_speed_ghz"] else None,
                processor_cores=processor_specs["cores"],
                processor_threads=processor_specs["threads"],
                processor_cache=f"{processor_specs['cache_mb']} MB" if processor_specs["cache_mb"] else None,

                # Memory
                memory_size_gb=memory_specs["size_gb"],
                memory_type=memory_specs["type"],
                memory_speed=f"{memory_specs['speed_mts']} MT/s" if memory_specs["speed_mts"] else None,
                memory_slots=tech_specs.get("Memory slots", ""),
                memory_configuration=memory_specs["configuration"],

                # Storage
                storage_size_gb=storage_specs["size_gb"],
                storage_type=storage_specs["type"],
                storage_interface=storage_specs["interface"],

                # Display
                display_size_inches=display_specs["size_inches"],
                display_resolution=display_specs["resolution"],
                display_resolution_standard=display_specs["resolution_standard"],
                display_touch=display_specs["touch"],
                display_panel_type=display_specs["panel_type"],
                display_brightness_nits=display_specs["brightness_nits"],
                display_color_gamut=f"{display_specs['color_gamut_percent']}% {display_specs['color_gamut_standard']}" if display_specs["color_gamut_percent"] else None,

                # Graphics
                graphics_integrated=self._extract_integrated_graphics(tech_specs.get("Graphics", "")),
                graphics_discrete=self._extract_discrete_graphics(tech_specs.get("Graphics", "")),

                # Physical
                width_inches=physical_specs["width_inches"],
                depth_inches=physical_specs["depth_inches"],
                height_front_inches=physical_specs["height_front_inches"],
                height_rear_inches=physical_specs["height_rear_inches"],
                weight_lbs=physical_specs["weight_lbs"],

                # Connectivity
                usb_c_ports=connectivity_specs["usb_c_ports"],
                usb_a_ports=connectivity_specs["usb_a_ports"],
                hdmi_ports=connectivity_specs["hdmi_ports"],
                ethernet_port=connectivity_specs["ethernet_port"],
                audio_jack=connectivity_specs["audio_jack"],
                wifi_standard=connectivity_specs["wifi_standard"],
                bluetooth_version=connectivity_specs["bluetooth_version"],

                # Features
                fingerprint_reader="fingerprint" in tech_specs.get("Finger print reader", "").lower(),
                backlit_keyboard="backlit" in tech_specs.get("Keyboard", "").lower(),
                touchpad_type=tech_specs.get("Pointing device", ""),
                webcam_resolution=self._extract_webcam_resolution(tech_specs.get("Webcam", "")),

                # Power
                battery_capacity_wh=self._extract_battery_capacity(tech_specs.get("Battery", "")),
                battery_cells=self._extract_battery_cells(tech_specs.get("Battery", "")),
                power_adapter_watts=self._extract_power_watts(tech_specs.get("Power supply", "")),

                # System
                operating_system=tech_specs.get("Operating system", ""),
                color=tech_specs.get("Color", ""),
                warranty_years=self._extract_warranty_years(tech_specs.get("Warranty", "")),

                # Raw data preservation
                raw_tech_specs=tech_specs,
                raw_pdp_summary=pdp_summary,
                raw_hero_snapshot=variant_data.get("hero_snapshot", {}),

                # Configuration path
                configuration_path=variant_data.get("sequence", []),

                variant_scraped_at=variant_timestamp
            )

            db.add(variant)
            db.flush()

            # Create price history entry
            if variant.sale_price:
                price_history = EnhancedPriceHistory(
                    variant_id=variant.id,
                    list_price=variant.list_price or Decimal(0),
                    sale_price=variant.sale_price,
                    discount_percentage=variant.discount_percentage,
                    savings_amount=variant.savings_amount,
                    stock_status=variant.stock_status,
                    estimated_ship_days=variant.estimated_ship_days,
                    scraped_at=variant_timestamp or datetime.utcnow(),
                    source_url=variant.variant_url
                )
                db.add(price_history)

            return variant

        except Exception as e:
            logger.error(f"Error processing variant: {e}")
            return None

    def _process_care_packages(self, db: Session, product_id: str, care_packages: List[Dict[str, Any]]) -> int:
        """Process care packages for a product"""
        count = 0
        try:
            for care_pack in care_packages:
                care_package = EnhancedCarePackage(
                    enhanced_product_id=product_id,
                    tier=care_pack.get("tier", ""),
                    description=care_pack.get("description", ""),
                    sale_price=self.clean_price_string(care_pack.get("sale_price")),
                    duration_years=self._extract_duration_years(care_pack.get("description", ""))
                )
                db.add(care_package)
                count += 1
        except Exception as e:
            logger.error(f"Error processing care packages: {e}")

        return count

    def _process_variant_offers(self, db: Session, variant_id: str, offers: List[str]) -> int:
        """Process offers for a variant"""
        count = 0
        try:
            for offer_text in offers:
                # Determine offer type
                offer_type = "general"
                if "shipping" in offer_text.lower():
                    offer_type = "shipping"
                elif "$" in offer_text or "%" in offer_text:
                    offer_type = "discount"
                elif "printer" in offer_text.lower() or "bundle" in offer_text.lower():
                    offer_type = "bundle"

                offer = VariantOffer(
                    configuration_variant_id=variant_id,
                    offer_text=offer_text,
                    offer_type=offer_type,
                    is_active=True
                )
                db.add(offer)
                count += 1
        except Exception as e:
            logger.error(f"Error processing variant offers: {e}")

        return count

    # Helper methods for specific extractions
    def _extract_ship_days(self, delivery_text: str) -> Optional[int]:
        """Extract estimated shipping days"""
        if not delivery_text:
            return None

        try:
            # Look for patterns like "Ships on Sep. 18, 25" -> assume 2 days
            if "ships" in delivery_text.lower():
                return 2  # Default for "ships on" messages
        except:
            pass
        return None

    def _extract_integrated_graphics(self, graphics_text: str) -> Optional[str]:
        """Extract integrated graphics info"""
        if not graphics_text:
            return None

        try:
            # Look for "Integrated:" section
            if "Integrated:" in graphics_text:
                integrated_part = graphics_text.split("Integrated:")[1].split("Discrete:")[0] if "Discrete:" in graphics_text else graphics_text.split("Integrated:")[1]
                return integrated_part.strip()
        except:
            pass
        return None

    def _extract_discrete_graphics(self, graphics_text: str) -> Optional[str]:
        """Extract discrete graphics info"""
        if not graphics_text:
            return None

        try:
            # Look for "Discrete:" section
            if "Discrete:" in graphics_text:
                discrete_part = graphics_text.split("Discrete:")[1]
                return discrete_part.strip()
        except:
            pass
        return None

    def _extract_webcam_resolution(self, webcam_text: str) -> Optional[str]:
        """Extract webcam resolution"""
        if not webcam_text:
            return None

        try:
            # Look for patterns like "5 MP"
            resolution_match = re.search(r'(\d+)\s*MP', webcam_text, re.IGNORECASE)
            if resolution_match:
                return f"{resolution_match.group(1)} MP"
        except:
            pass
        return None

    def _extract_battery_capacity(self, battery_text: str) -> Optional[int]:
        """Extract battery capacity in Wh"""
        if not battery_text:
            return None

        try:
            wh_match = re.search(r'(\d+)\s*Wh', battery_text, re.IGNORECASE)
            if wh_match:
                return int(wh_match.group(1))
        except:
            pass
        return None

    def _extract_battery_cells(self, battery_text: str) -> Optional[int]:
        """Extract number of battery cells"""
        if not battery_text:
            return None

        try:
            cells_match = re.search(r'(\d+)-cell', battery_text, re.IGNORECASE)
            if cells_match:
                return int(cells_match.group(1))
        except:
            pass
        return None

    def _extract_power_watts(self, power_text: str) -> Optional[int]:
        """Extract power adapter wattage"""
        if not power_text:
            return None

        try:
            watts_match = re.search(r'(\d+)\s*W', power_text, re.IGNORECASE)
            if watts_match:
                return int(watts_match.group(1))
        except:
            pass
        return None

    def _extract_warranty_years(self, warranty_text: str) -> Optional[int]:
        """Extract warranty period in years"""
        if not warranty_text:
            return None

        try:
            years_match = re.search(r'(\d+)\s*year', warranty_text, re.IGNORECASE)
            if years_match:
                return int(years_match.group(1))
        except:
            pass
        return None

    def _extract_duration_years(self, description: str) -> Optional[int]:
        """Extract duration in years from care package description"""
        if not description:
            return None

        try:
            years_match = re.search(r'(\d+)\s*year', description, re.IGNORECASE)
            if years_match:
                return int(years_match.group(1))
        except:
            pass
        return None


# Global instance
scraped_data_processor = ScrapedDataProcessor()