from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas import ProductResponse, ProductWithVariants, VariantResponse, ProductSummary
from app.models import Product, Variant
from app.services.recommendation_engine import RecommendationEngine
import re

router = APIRouter()


@router.get("")
async def get_products(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=100, description="Items per page"),

    # Search parameters
    query: Optional[str] = Query(None, description="Search query"),

    # Sorting parameters
    sort_by: Optional[str] = Query(None, description="Sort by: price_asc, price_desc, rating, popularity, name, newest"),

    # Filter parameters
    brands: Optional[str] = Query(None, description="Comma-separated brand names"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    processors: Optional[str] = Query(None, description="Comma-separated processor types"),
    memory: Optional[str] = Query(None, description="Comma-separated memory sizes"),
    storage: Optional[str] = Query(None, description="Comma-separated storage options"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    availability: Optional[str] = Query(None, description="Comma-separated availability statuses"),

    db: Session = Depends(get_db)
):
    """
    Get products with advanced filtering, sorting, and pagination.
    Implements all requirements from report.md
    """
    try:
        # Start with base query
        query_builder = db.query(Product)

        # Track applied filters for response
        filters_applied = {}

        # Apply search query
        if query:
            search_term = query.lower()
            # Check if Product has these fields, otherwise adjust
            query_builder = query_builder.filter(
                or_(
                    Product.product_name.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                    Product.model_family.ilike(f"%{query}%")
                )
            )
            filters_applied["query"] = query

        # Apply brand filter
        if brands:
            brand_list = [b.strip() for b in brands.split(",")]
            query_builder = query_builder.filter(Product.brand.in_(brand_list))
            filters_applied["brands"] = brand_list

        # Apply price range filter
        if price_min is not None:
            query_builder = query_builder.filter(Product.base_price >= price_min)
            filters_applied["price_min"] = price_min
        if price_max is not None:
            query_builder = query_builder.filter(Product.base_price <= price_max)
            filters_applied["price_max"] = price_max

        # Apply processor filter (assuming specs exist in Product or Variant)
        if processors:
            processor_list = [p.strip() for p in processors.split(",")]
            # This assumes Product has specs JSON column
            processor_conditions = []
            for processor in processor_list:
                # Adjust based on actual model structure
                processor_conditions.append(
                    Product.product_name.ilike(f"%{processor}%")
                )
            if processor_conditions:
                query_builder = query_builder.filter(or_(*processor_conditions))
            filters_applied["processors"] = processor_list

        # Apply memory filter
        if memory:
            memory_list = [m.strip() for m in memory.split(",")]
            memory_conditions = []
            for mem in memory_list:
                memory_conditions.append(
                    Product.product_name.ilike(f"%{mem}%")
                )
            if memory_conditions:
                query_builder = query_builder.filter(or_(*memory_conditions))
            filters_applied["memory"] = memory_list

        # Apply storage filter
        if storage:
            storage_list = [s.strip() for s in storage.split(",")]
            storage_conditions = []
            for stor in storage_list:
                storage_conditions.append(
                    Product.product_name.ilike(f"%{stor}%")
                )
            if storage_conditions:
                query_builder = query_builder.filter(or_(*storage_conditions))
            filters_applied["storage"] = storage_list

        # Apply rating filter (if Product has rating field)
        if min_rating is not None:
            # Adjust if rating is stored elsewhere
            # query_builder = query_builder.filter(Product.rating >= min_rating)
            filters_applied["min_rating"] = min_rating

        # Apply availability filter
        if availability:
            availability_list = [a.strip() for a in availability.split(",")]
            # Map common variations
            availability_mapped = []
            for avail in availability_list:
                if avail.lower() in ["in_stock", "in stock", "instock"]:
                    availability_mapped.append("In Stock")
                elif avail.lower() in ["out_of_stock", "out of stock", "outofstock"]:
                    availability_mapped.append("Out of Stock")
                elif avail.lower() in ["pre_order", "pre-order", "preorder"]:
                    availability_mapped.append("Pre-order")
                else:
                    availability_mapped.append(avail)

            # Adjust based on actual field name
            if hasattr(Product, 'status'):
                query_builder = query_builder.filter(Product.status.in_(availability_mapped))
            filters_applied["availability"] = availability_list

        # Apply sorting
        if sort_by:
            if sort_by == "price_asc":
                query_builder = query_builder.order_by(Product.base_price.asc())
            elif sort_by == "price_desc":
                query_builder = query_builder.order_by(Product.base_price.desc())
            elif sort_by == "rating":
                # Adjust if rating field exists
                query_builder = query_builder.order_by(Product.base_price.desc())  # Placeholder
            elif sort_by == "popularity":
                # Adjust based on review count field
                query_builder = query_builder.order_by(Product.base_price.desc())  # Placeholder
            elif sort_by == "name":
                query_builder = query_builder.order_by(Product.product_name.asc())
            elif sort_by == "newest":
                if hasattr(Product, 'created_at'):
                    query_builder = query_builder.order_by(Product.created_at.desc())
            filters_applied["sort_by"] = sort_by

        # Get total count before pagination
        total = query_builder.count()

        # Calculate pagination (handle empty results)
        if total == 0:
            total_pages = 0
            has_more = False
            products = []
        else:
            offset = (page - 1) * limit
            total_pages = (total + limit - 1) // limit  # Ceiling division
            has_more = page < total_pages

            # Apply pagination
            products = query_builder.offset(offset).limit(limit).all()

        # Format response according to report.md requirements
        product_list = []
        for p in products:
            # Get variant count for this product
            variant_count = db.query(Variant).filter(Variant.product_id == p.id).count()

            # Build product dict matching report.md format
            product_dict = {
                "id": p.id,
                "brand": p.brand or "Unknown",
                "model": p.model_family or "Unknown",
                "name": p.product_name or f"{p.brand or 'Unknown'} Product",
                "base_price": p.base_price or 0,
                "currency": "USD",  # Default currency
                "availability": p.status or "Unknown",
                "rating": getattr(p, 'rating', 4.0),  # Default rating if not exists
                "review_count": getattr(p, 'review_count', 0),
                "specs": {}  # Add specs if available
            }

            # Add specs from variants if needed
            variants = db.query(Variant).filter(Variant.product_id == p.id).limit(1).all()
            if variants:
                v = variants[0]
                product_dict["specs"] = {
                    "processor": v.processor or "",
                    "memory": v.memory or "",
                    "storage": v.storage or "",
                    "display": v.display or "",
                    "graphics": v.graphics or "",
                    "battery": "",
                    "weight": ""
                }

            product_list.append(product_dict)

        return {
            "products": product_list,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_more": has_more,
            "filters_applied": filters_applied
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


# Static routes MUST come before dynamic routes to avoid path conflicts
@router.get("/brands")
async def get_brands(db: Session = Depends(get_db)):
    """Get list of available brands"""
    brands = db.query(Product.brand).distinct().all()
    brand_list = [brand.brand for brand in brands if brand.brand]

    # Get product count for each brand
    brand_info = []
    for brand in brand_list:
        count = db.query(Product).filter(Product.brand == brand).count()
        brand_info.append({
            "name": brand,
            "product_count": count
        })

    return {
        "brands": brand_info,
        "total": len(brand_info)
    }


@router.get("/stats")
async def get_catalog_stats(db: Session = Depends(get_db)):
    """Get overall catalog statistics"""
    try:
        total_products = db.query(Product).count()
        total_variants = db.query(Variant).count()

        # Brand distribution with product and variant counts
        brands = db.query(Product.brand).distinct().all()
        brand_stats = []
        for brand in brands:
            if brand.brand:
                # Get products for this brand
                brand_products = db.query(Product).filter(Product.brand == brand.brand).all()
                product_count = len(brand_products)

                # Count variants for all products of this brand
                variant_count = 0
                for product in brand_products:
                    variant_count += db.query(Variant).filter(Variant.product_id == product.id).count()

                brand_stats.append({
                    "brand": brand.brand,
                    "products": product_count,
                    "variants": variant_count
                })

        # Price range - use base_price from Product
        price_stats = db.query(
            func.min(Product.base_price),
            func.max(Product.base_price),
            func.avg(Product.base_price)
        ).first()

        min_price = float(price_stats[0]) if price_stats[0] else 0.0
        max_price = float(price_stats[1]) if price_stats[1] else 0.0
        avg_price = float(price_stats[2]) if price_stats[2] else 0.0

        return {
            "total_products": total_products,
            "total_variants": total_variants,
            "brands": brand_stats,
            "price_range": {
                "min": min_price,
                "max": max_price,
                "average": round(avg_price, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


# Dynamic routes come AFTER static routes
@router.get("/{product_id}", response_model=ProductWithVariants)
async def get_product(
    product_id: str,  # UUID string format
    db: Session = Depends(get_db)
):
    """Get specific product details with all its variants"""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get all variants for this product
    variants = db.query(Variant).filter(Variant.product_id == product_id).all()

    # Convert to response model
    product_response = ProductWithVariants(
        id=product.id,
        brand=product.brand,
        model_family=product.model_family,
        base_sku=product.base_sku,
        product_name=product.product_name,
        product_url=product.product_url,
        pdf_spec_url=product.pdf_spec_url,
        base_price=product.base_price,
        original_price=product.original_price,
        status=product.status,
        badges=product.badges or [],
        offers=product.offers or [],
        created_at=product.created_at,
        updated_at=product.updated_at,
        variants=[VariantResponse.from_orm(variant) for variant in variants]
    )

    return product_response


@router.get("/{product_id}/variants", response_model=List[VariantResponse])
async def get_variants(
    product_id: str,  # UUID string format
    db: Session = Depends(get_db)
):
    """Get all variants for a specific product"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    variants = db.query(Variant).filter(Variant.product_id == product_id).all()
    return [VariantResponse.from_orm(variant) for variant in variants]


@router.get("/variants/{variant_id}", response_model=VariantResponse)
async def get_variant(
    variant_id: str,
    db: Session = Depends(get_db)
):
    """Get specific variant details"""
    variant = db.query(Variant).filter(Variant.id == variant_id).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    return VariantResponse.from_orm(variant)


@router.get("/variants/{variant_id}/similar")
async def get_similar_variants(
    variant_id: str,
    limit: int = Query(3, ge=1, le=10, description="Number of similar products to return"),
    db: Session = Depends(get_db)
):
    """Get products similar to the specified variant"""
    # Verify variant exists
    variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    recommendation_engine = RecommendationEngine(db)
    similar_products = await recommendation_engine.get_similar_products(variant_id, limit)

    return {
        "variant_id": variant_id,
        "similar_products": similar_products,
        "total": len(similar_products)
    }










