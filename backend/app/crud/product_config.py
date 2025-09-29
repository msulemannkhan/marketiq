from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import and_, or_, func, desc, asc
from datetime import datetime, timedelta
import json
import hashlib

from app.models.product_config import (
    ProductConfiguration, ConfigurationVariant, CarePackage,
    VariantOffer, PriceSnapshot
)
from app.schemas.product_config import (
    ProductConfigurationCreate, ProductConfigurationUpdate,
    ConfigurationVariantCreate, ConfigurationVariantUpdate,
    CarePackageCreate, VariantOfferCreate, PriceSnapshotCreate,
    ConfigurationVariantFilter
)


# ProductConfiguration CRUD
class ProductConfigurationCRUD:

    @staticmethod
    def create(db: Session, obj_in: ProductConfigurationCreate) -> ProductConfiguration:
        """Create a new product configuration"""
        db_obj = ProductConfiguration(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, product_config_id: str) -> Optional[ProductConfiguration]:
        """Get product configuration by ID"""
        return db.query(ProductConfiguration).filter(
            ProductConfiguration.id == product_config_id
        ).first()

    @staticmethod
    def get_by_url(db: Session, base_url: str) -> Optional[ProductConfiguration]:
        """Get product configuration by base URL"""
        return db.query(ProductConfiguration).filter(
            ProductConfiguration.base_url == base_url
        ).first()

    @staticmethod
    def get_by_brand_model(db: Session, brand: str, model_family: str) -> List[ProductConfiguration]:
        """Get product configurations by brand and model family"""
        return db.query(ProductConfiguration).filter(
            and_(
                ProductConfiguration.brand == brand,
                ProductConfiguration.model_family == model_family
            )
        ).all()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        brand: Optional[str] = None,
        model_family: Optional[str] = None
    ) -> List[ProductConfiguration]:
        """Get all product configurations with optional filtering"""
        query = db.query(ProductConfiguration)

        if brand:
            query = query.filter(ProductConfiguration.brand == brand)
        if model_family:
            query = query.filter(ProductConfiguration.model_family == model_family)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_with_variants(db: Session, product_config_id: str) -> Optional[ProductConfiguration]:
        """Get product configuration with all variants"""
        return db.query(ProductConfiguration).options(
            selectinload(ProductConfiguration.configuration_variants),
            selectinload(ProductConfiguration.care_packages)
        ).filter(ProductConfiguration.id == product_config_id).first()

    @staticmethod
    def update(
        db: Session,
        product_config_id: str,
        obj_in: ProductConfigurationUpdate
    ) -> Optional[ProductConfiguration]:
        """Update product configuration"""
        db_obj = db.query(ProductConfiguration).filter(
            ProductConfiguration.id == product_config_id
        ).first()

        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.commit()
            db.refresh(db_obj)

        return db_obj

    @staticmethod
    def delete(db: Session, product_config_id: str) -> bool:
        """Delete product configuration"""
        db_obj = db.query(ProductConfiguration).filter(
            ProductConfiguration.id == product_config_id
        ).first()

        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False


# ConfigurationVariant CRUD
class ConfigurationVariantCRUD:

    @staticmethod
    def create(db: Session, obj_in: ConfigurationVariantCreate) -> ConfigurationVariant:
        """Create a new configuration variant"""
        db_obj = ConfigurationVariant(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get(db: Session, variant_id: str) -> Optional[ConfigurationVariant]:
        """Get configuration variant by ID"""
        return db.query(ConfigurationVariant).filter(
            ConfigurationVariant.id == variant_id
        ).first()

    @staticmethod
    def get_by_sku(db: Session, variant_sku: str) -> Optional[ConfigurationVariant]:
        """Get configuration variant by SKU"""
        return db.query(ConfigurationVariant).filter(
            ConfigurationVariant.variant_sku == variant_sku
        ).first()

    @staticmethod
    def get_by_product_config(db: Session, product_config_id: str) -> List[ConfigurationVariant]:
        """Get all variants for a product configuration"""
        return db.query(ConfigurationVariant).filter(
            ConfigurationVariant.product_configuration_id == product_config_id
        ).all()

    @staticmethod
    def search_variants(
        db: Session,
        filters: ConfigurationVariantFilter,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[ConfigurationVariant]:
        """Search variants with advanced filtering"""
        query = db.query(ConfigurationVariant)

        # Join with ProductConfiguration for brand and model filtering
        if filters.brand or filters.model_family:
            query = query.join(ProductConfiguration)

        # Apply filters
        if filters.brand:
            query = query.filter(ProductConfiguration.brand == filters.brand)

        if filters.model_family:
            query = query.filter(ProductConfiguration.model_family == filters.model_family)

        if filters.processor_family:
            query = query.filter(
                ConfigurationVariant.processor_family.ilike(f"%{filters.processor_family}%")
            )

        if filters.memory_size_min:
            query = query.filter(
                ConfigurationVariant.memory.ilike(f"%{filters.memory_size_min}%")
            )

        if filters.price_min:
            query = query.filter(ConfigurationVariant.sale_price >= filters.price_min)

        if filters.price_max:
            query = query.filter(ConfigurationVariant.sale_price <= filters.price_max)

        if filters.display_size:
            query = query.filter(
                ConfigurationVariant.display.ilike(f"%{filters.display_size}%")
            )

        if filters.stock_status:
            query = query.filter(ConfigurationVariant.stock_status == filters.stock_status)

        if filters.has_discount is not None:
            if filters.has_discount:
                query = query.filter(ConfigurationVariant.discount_percentage > 0)
            else:
                query = query.filter(
                    or_(
                        ConfigurationVariant.discount_percentage == 0,
                        ConfigurationVariant.discount_percentage.is_(None)
                    )
                )

        # Apply ordering
        order_column = getattr(ConfigurationVariant, order_by, ConfigurationVariant.created_at)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_with_offers_and_prices(db: Session, variant_id: str) -> Optional[ConfigurationVariant]:
        """Get variant with all related offers and price snapshots"""
        return db.query(ConfigurationVariant).options(
            selectinload(ConfigurationVariant.variant_offers),
            selectinload(ConfigurationVariant.price_snapshots)
        ).filter(ConfigurationVariant.id == variant_id).first()

    @staticmethod
    def update(
        db: Session,
        variant_id: str,
        obj_in: ConfigurationVariantUpdate
    ) -> Optional[ConfigurationVariant]:
        """Update configuration variant"""
        db_obj = db.query(ConfigurationVariant).filter(
            ConfigurationVariant.id == variant_id
        ).first()

        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.commit()
            db.refresh(db_obj)

        return db_obj

    @staticmethod
    def delete(db: Session, variant_id: str) -> bool:
        """Delete configuration variant"""
        db_obj = db.query(ConfigurationVariant).filter(
            ConfigurationVariant.id == variant_id
        ).first()

        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    @staticmethod
    def get_price_trends(
        db: Session,
        variant_id: str,
        days: int = 30
    ) -> List[PriceSnapshot]:
        """Get price trends for a variant over specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(PriceSnapshot).filter(
            and_(
                PriceSnapshot.configuration_variant_id == variant_id,
                PriceSnapshot.snapshot_date >= cutoff_date
            )
        ).order_by(PriceSnapshot.snapshot_date).all()


# CarePackage CRUD
class CarePackageCRUD:

    @staticmethod
    def create(db: Session, obj_in: CarePackageCreate) -> CarePackage:
        """Create a new care package"""
        db_obj = CarePackage(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_product_config(db: Session, product_config_id: str) -> List[CarePackage]:
        """Get all care packages for a product configuration"""
        return db.query(CarePackage).filter(
            CarePackage.product_configuration_id == product_config_id
        ).order_by(CarePackage.sale_price.asc().nullsfirst()).all()

    @staticmethod
    def delete_by_product_config(db: Session, product_config_id: str) -> int:
        """Delete all care packages for a product configuration"""
        deleted_count = db.query(CarePackage).filter(
            CarePackage.product_configuration_id == product_config_id
        ).delete()
        db.commit()
        return deleted_count


# VariantOffer CRUD
class VariantOfferCRUD:

    @staticmethod
    def create(db: Session, obj_in: VariantOfferCreate) -> VariantOffer:
        """Create a new variant offer"""
        db_obj = VariantOffer(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def create_multiple(db: Session, offers: List[str], variant_id: str) -> List[VariantOffer]:
        """Create multiple offers for a variant"""
        db_offers = []
        for offer_text in offers:
            # Determine offer type based on text content
            offer_type = "general"
            if "shipping" in offer_text.lower():
                offer_type = "shipping"
            elif "discount" in offer_text.lower() or "%" in offer_text or "$" in offer_text:
                offer_type = "discount"
            elif "printer" in offer_text.lower() or "buy" in offer_text.lower():
                offer_type = "bundle"

            offer_obj = VariantOffer(
                configuration_variant_id=variant_id,
                offer_text=offer_text,
                offer_type=offer_type
            )
            db_offers.append(offer_obj)

        db.add_all(db_offers)
        db.commit()
        for offer in db_offers:
            db.refresh(offer)

        return db_offers

    @staticmethod
    def get_active_by_variant(db: Session, variant_id: str) -> List[VariantOffer]:
        """Get all active offers for a variant"""
        return db.query(VariantOffer).filter(
            and_(
                VariantOffer.configuration_variant_id == variant_id,
                VariantOffer.is_active == True
            )
        ).all()


# PriceSnapshot CRUD
class PriceSnapshotCRUD:

    @staticmethod
    def create(db: Session, obj_in: PriceSnapshotCreate) -> PriceSnapshot:
        """Create a new price snapshot"""
        db_obj = PriceSnapshot(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_latest_by_variant(db: Session, variant_id: str) -> Optional[PriceSnapshot]:
        """Get the latest price snapshot for a variant"""
        return db.query(PriceSnapshot).filter(
            PriceSnapshot.configuration_variant_id == variant_id
        ).order_by(desc(PriceSnapshot.snapshot_date)).first()

    @staticmethod
    def get_price_history(
        db: Session,
        variant_id: str,
        days: int = 30
    ) -> List[PriceSnapshot]:
        """Get price history for a variant"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(PriceSnapshot).filter(
            and_(
                PriceSnapshot.configuration_variant_id == variant_id,
                PriceSnapshot.snapshot_date >= cutoff_date
            )
        ).order_by(PriceSnapshot.snapshot_date).all()


# Bulk Operations
class BulkProductConfigCRUD:

    @staticmethod
    def import_from_json(
        db: Session,
        json_data: Dict[str, Any],
        override_existing: bool = False
    ) -> Dict[str, Any]:
        """Import product configuration from JSON data"""
        result = {
            "success": False,
            "products_created": 0,
            "variants_created": 0,
            "care_packages_created": 0,
            "offers_created": 0,
            "errors": [],
            "warnings": []
        }

        try:
            # Extract base product info
            base_product = json_data.get("Base_Product", {})
            variants_data = json_data.get("Variants", [])
            collected_at_str = json_data.get("collected_at")

            if not base_product:
                result["errors"].append("No Base_Product found in JSON data")
                return result

            # Parse collected_at timestamp
            collected_at = datetime.fromisoformat(collected_at_str.replace("Z", "+00:00")) if collected_at_str else datetime.utcnow()

            # Extract brand and model from base product
            base_url = base_product.get("url", "")
            pdp_summary = base_product.get("pdp_summary", {})
            title = pdp_summary.get("title", "")

            # Determine brand and model from title
            brand = "Unknown"
            model_family = "Unknown"

            if "HP" in title:
                brand = "HP"
                if "ProBook" in title:
                    model_family = "ProBook 460" if "460" in title else "ProBook 440"
            elif "Lenovo" in title or "ThinkPad" in title:
                brand = "Lenovo"
                if "ThinkPad" in title:
                    model_family = "ThinkPad E14"

            # Check if product configuration already exists
            existing_config = ProductConfigurationCRUD.get_by_url(db, base_url)

            if existing_config and not override_existing:
                result["warnings"].append(f"Product configuration already exists for URL: {base_url}")
                return result

            # Create or update product configuration
            if existing_config and override_existing:
                # Update existing
                update_data = ProductConfigurationUpdate(
                    brand=brand,
                    model_family=model_family,
                    base_url=base_url,
                    variants_total=len(variants_data),
                    base_product_data=base_product,
                    raw_data=json_data
                )
                product_config = ProductConfigurationCRUD.update(db, str(existing_config.id), update_data)
            else:
                # Create new
                config_data = ProductConfigurationCreate(
                    brand=brand,
                    model_family=model_family,
                    base_url=base_url,
                    variants_total=len(variants_data),
                    collected_at=collected_at,
                    base_product_data=base_product,
                    raw_data=json_data
                )
                product_config = ProductConfigurationCRUD.create(db, config_data)
                result["products_created"] = 1

            # Process care packages from base product
            care_packs = base_product.get("hero_snapshot", {}).get("care_packs", [])
            if care_packs:
                # Delete existing care packages if updating
                if existing_config:
                    CarePackageCRUD.delete_by_product_config(db, str(product_config.id))

                for care_pack in care_packs:
                    care_package_data = CarePackageCreate(
                        product_configuration_id=product_config.id,
                        tier=care_pack.get("tier", ""),
                        description=care_pack.get("description", ""),
                        sale_price=float(care_pack.get("sale_price", "0").replace("$", "").replace(",", "")) if care_pack.get("sale_price") else None
                    )
                    CarePackageCRUD.create(db, care_package_data)
                    result["care_packages_created"] += 1

            # Process variants
            for variant_data in variants_data:
                try:
                    variant_id = variant_data.get("variant_id", "")
                    pdp_summary = variant_data.get("pdp_summary", {})
                    hero_snapshot = variant_data.get("hero_snapshot", {})
                    tech_specs = variant_data.get("tech_specs", {})
                    timestamp_str = variant_data.get("timestamp")

                    # Parse pricing
                    list_price_str = pdp_summary.get("list_price", "0").replace("$", "").replace(",", "")
                    sale_price_str = pdp_summary.get("sale_price", "0").replace("$", "").replace(",", "")
                    savings_str = pdp_summary.get("save_text", "").replace("you save $", "").replace(",", "")
                    discount_str = pdp_summary.get("discount_label", "").replace("% OFF", "")

                    try:
                        list_price = float(list_price_str) if list_price_str else 0.0
                        sale_price = float(sale_price_str) if sale_price_str else 0.0
                        savings_amount = float(savings_str) if savings_str else 0.0
                        discount_percentage = int(discount_str) if discount_str.isdigit() else 0
                    except (ValueError, TypeError):
                        list_price = sale_price = savings_amount = 0.0
                        discount_percentage = 0

                    # Parse timestamp
                    data_timestamp = None
                    if timestamp_str:
                        try:
                            data_timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                        except:
                            pass

                    # Create variant
                    variant_create_data = ConfigurationVariantCreate(
                        product_configuration_id=product_config.id,
                        variant_id=variant_id,
                        variant_sku=pdp_summary.get("sku_hint", ""),
                        variant_url=variant_data.get("url", ""),
                        configuration_sequence=[item.get("label", "") for item in variant_data.get("sequence", [])],

                        # PDP Summary
                        title=pdp_summary.get("title", ""),
                        usage_label=pdp_summary.get("usage_label", ""),
                        rating=float(pdp_summary.get("rating")) if pdp_summary.get("rating") else None,
                        review_count=int(pdp_summary.get("review_count")) if pdp_summary.get("review_count") else None,

                        # Pricing
                        msrp_label=pdp_summary.get("msrp_label", ""),
                        list_price=list_price,
                        sale_price=sale_price,
                        discount_percentage=discount_percentage,
                        savings_amount=savings_amount,

                        # Stock
                        stock_status=pdp_summary.get("stock", ""),
                        delivery_info=pdp_summary.get("delivery", ""),
                        stock_icon=pdp_summary.get("stock_icon", ""),

                        # Hero snapshot
                        offers=hero_snapshot.get("offers", []),
                        rewards_badge=hero_snapshot.get("rewards_badge", ""),
                        sustainability_badge=hero_snapshot.get("sustainability_badge", ""),
                        add_to_compare=hero_snapshot.get("add_to_compare", False),

                        # Technical specs
                        operating_system=tech_specs.get("Operating system", ""),
                        processor_family=tech_specs.get("Processor family", ""),
                        processor=tech_specs.get("Processor", ""),
                        graphics=tech_specs.get("Graphics", ""),
                        memory=tech_specs.get("Memory", ""),
                        memory_slots=tech_specs.get("Memory slots", ""),
                        internal_drive=tech_specs.get("Internal drive", ""),
                        display=tech_specs.get("Display", ""),
                        external_io_ports=tech_specs.get("External I/O Ports", ""),
                        audio_features=tech_specs.get("Audio Features", ""),
                        webcam=tech_specs.get("Webcam", ""),
                        keyboard=tech_specs.get("Keyboard", ""),
                        pointing_device=tech_specs.get("Pointing device", ""),
                        wireless_technology=tech_specs.get("Wireless technology", ""),
                        network_interface=tech_specs.get("Network interface", ""),
                        power_supply=tech_specs.get("Power supply", ""),
                        battery=tech_specs.get("Battery", ""),
                        color=tech_specs.get("Color", ""),
                        fingerprint_reader=tech_specs.get("Finger print reader", ""),
                        energy_efficiency=tech_specs.get("Energy efficiency", ""),
                        dimensions=tech_specs.get("Dimensions (W X D X H)", ""),
                        weight=tech_specs.get("Weight", ""),
                        warranty=tech_specs.get("Warranty", ""),

                        # Software and management
                        security_software_license=tech_specs.get("Security software license", ""),
                        software_included=tech_specs.get("Software included", ""),
                        manageability_features=tech_specs.get("Manageability Features", ""),
                        security_management=tech_specs.get("Security management", ""),
                        support_service_included=tech_specs.get("Support Service Included", ""),
                        sustainable_impact_specs=tech_specs.get("Sustainable Impact Specifications", ""),

                        # JSON data
                        pdp_summary_data=pdp_summary,
                        hero_snapshot_data=hero_snapshot,
                        tech_specs_data=tech_specs,
                        cto_selected=hero_snapshot.get("cto_selected", {}),

                        data_timestamp=data_timestamp
                    )

                    variant = ConfigurationVariantCRUD.create(db, variant_create_data)
                    result["variants_created"] += 1

                    # Create offers for this variant
                    offers = hero_snapshot.get("offers", [])
                    if offers:
                        variant_offers = VariantOfferCRUD.create_multiple(db, offers, str(variant.id))
                        result["offers_created"] += len(variant_offers)

                    # Create initial price snapshot
                    if sale_price > 0:
                        price_snapshot_data = PriceSnapshotCreate(
                            configuration_variant_id=variant.id,
                            list_price=list_price,
                            sale_price=sale_price,
                            discount_percentage=discount_percentage,
                            savings_amount=savings_amount,
                            stock_status=pdp_summary.get("stock", ""),
                            delivery_info=pdp_summary.get("delivery", ""),
                            snapshot_date=data_timestamp or datetime.utcnow()
                        )
                        PriceSnapshotCRUD.create(db, price_snapshot_data)

                except Exception as e:
                    result["errors"].append(f"Error processing variant {variant_data.get('variant_id', 'unknown')}: {str(e)}")
                    continue

            result["success"] = True

        except Exception as e:
            result["errors"].append(f"Failed to import JSON data: {str(e)}")
            # Rollback changes if there was an error
            db.rollback()

        return result


# Analytics and Statistics
class ProductConfigAnalytics:

    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """Get comprehensive statistics for product configurations"""
        stats = {}

        # Basic counts
        stats["total_products"] = db.query(ProductConfiguration).count()
        stats["total_variants"] = db.query(ConfigurationVariant).count()

        # Brand and model counts
        brands = db.query(ProductConfiguration.brand).distinct().all()
        stats["brands_count"] = len(brands)
        stats["brands"] = [brand[0] for brand in brands]

        model_families = db.query(ProductConfiguration.model_family).distinct().all()
        stats["model_families_count"] = len(model_families)
        stats["model_families"] = [model[0] for model in model_families]

        # Average variants per product
        if stats["total_products"] > 0:
            stats["average_variants_per_product"] = stats["total_variants"] / stats["total_products"]
        else:
            stats["average_variants_per_product"] = 0.0

        # Price statistics
        price_query = db.query(
            func.min(ConfigurationVariant.sale_price).label("min_price"),
            func.max(ConfigurationVariant.sale_price).label("max_price"),
            func.avg(ConfigurationVariant.sale_price).label("avg_price")
        ).filter(ConfigurationVariant.sale_price > 0).first()

        if price_query and price_query.min_price:
            stats["price_range"] = {
                "min": float(price_query.min_price),
                "max": float(price_query.max_price),
                "average": float(price_query.avg_price) if price_query.avg_price else 0.0
            }
        else:
            stats["price_range"] = {"min": 0.0, "max": 0.0, "average": 0.0}

        # Data freshness
        latest_collection = db.query(
            func.max(ProductConfiguration.collected_at)
        ).scalar()

        if latest_collection:
            stats["latest_collection_date"] = latest_collection
            hours_since = (datetime.utcnow() - latest_collection).total_seconds() / 3600
            stats["data_freshness_hours"] = hours_since
        else:
            stats["latest_collection_date"] = None
            stats["data_freshness_hours"] = None

        return stats

    @staticmethod
    def get_brand_comparison(db: Session) -> Dict[str, Any]:
        """Get comparison statistics between brands"""
        comparison = {}

        brands = db.query(ProductConfiguration.brand).distinct().all()

        for brand_tuple in brands:
            brand = brand_tuple[0]

            # Product count
            product_count = db.query(ProductConfiguration).filter(
                ProductConfiguration.brand == brand
            ).count()

            # Variant count
            variant_count = db.query(ConfigurationVariant).join(ProductConfiguration).filter(
                ProductConfiguration.brand == brand
            ).count()

            # Price statistics
            price_stats = db.query(
                func.min(ConfigurationVariant.sale_price).label("min_price"),
                func.max(ConfigurationVariant.sale_price).label("max_price"),
                func.avg(ConfigurationVariant.sale_price).label("avg_price")
            ).join(ProductConfiguration).filter(
                and_(
                    ProductConfiguration.brand == brand,
                    ConfigurationVariant.sale_price > 0
                )
            ).first()

            comparison[brand] = {
                "product_count": product_count,
                "variant_count": variant_count,
                "price_stats": {
                    "min": float(price_stats.min_price) if price_stats.min_price else 0.0,
                    "max": float(price_stats.max_price) if price_stats.max_price else 0.0,
                    "average": float(price_stats.avg_price) if price_stats.avg_price else 0.0
                } if price_stats else {"min": 0.0, "max": 0.0, "average": 0.0}
            }

        return comparison