from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.schemas.variant import VariantComparison, VariantResponse
from app.models import Variant, Product

router = APIRouter()


@router.post("/compare", response_model=VariantComparison)
async def compare_variants(
    variant_ids: List[str],
    db: Session = Depends(get_db)
):
    """Compare multiple variants side by side"""
    if len(variant_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 variants required for comparison")

    if len(variant_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 variants can be compared at once")

    # Fetch variants
    variants = db.query(Variant).join(Product).filter(Variant.id.in_(variant_ids)).all()

    if len(variants) != len(variant_ids):
        missing_ids = set(variant_ids) - {str(v.id) for v in variants}
        raise HTTPException(
            status_code=404,
            detail=f"Variants not found: {list(missing_ids)}"
        )

    # Convert to response models
    variant_responses = [VariantResponse.from_orm(variant) for variant in variants]

    # Build comparison matrix
    comparison_matrix = _build_comparison_matrix(variants)

    # Identify differences
    differences = _identify_differences(variants)

    return VariantComparison(
        variants=variant_responses,
        comparison_matrix=comparison_matrix,
        differences=differences
    )


@router.get("/compare/suggestions")
async def get_comparison_suggestions(
    variant_id: str,
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get suggested variants for comparison"""
    # Verify base variant exists
    base_variant = db.query(Variant).filter(Variant.id == variant_id).first()
    if not base_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Find similar variants based on criteria
    query = db.query(Variant).join(Product).filter(
        Variant.id != variant_id  # Exclude the base variant
    )

    # Similar price range (±25%)
    if base_variant.price:
        price_min = base_variant.price * 0.75
        price_max = base_variant.price * 1.25
        query = query.filter(
            Variant.price >= price_min,
            Variant.price <= price_max
        )

    # Prefer different brands for comparison
    query = query.filter(Product.brand != base_variant.product.brand)

    suggestions = query.limit(limit).all()

    # If not enough different brands, include same brand
    if len(suggestions) < limit:
        same_brand_query = db.query(Variant).join(Product).filter(
            Variant.id != variant_id,
            Product.brand == base_variant.product.brand
        )

        if base_variant.price:
            same_brand_query = same_brand_query.filter(
                Variant.price >= price_min,
                Variant.price <= price_max
            )

        additional_suggestions = same_brand_query.limit(limit - len(suggestions)).all()
        suggestions.extend(additional_suggestions)

    return {
        "base_variant_id": variant_id,
        "suggestions": [
            {
                "id": str(variant.id),
                "product_name": variant.product.product_name,
                "brand": variant.product.brand,
                "processor": variant.processor,
                "memory": variant.memory,
                "price": float(variant.price) if variant.price else None,
                "reason": _get_comparison_reason(base_variant, variant)
            }
            for variant in suggestions
        ]
    }


def _build_comparison_matrix(variants: List[Variant]) -> Dict[str, List[str]]:
    """Build a matrix showing all comparable attributes"""
    matrix = {}

    # Define attributes to compare
    attributes = [
        ("Product Name", lambda v: v.product.product_name),
        ("Brand", lambda v: v.product.brand),
        ("Model Family", lambda v: v.product.model_family),
        ("Processor", lambda v: v.processor or "Not specified"),
        ("Processor Family", lambda v: v.processor_family or "Not specified"),
        ("Memory", lambda v: v.memory or "Not specified"),
        ("Memory Size (GB)", lambda v: str(v.memory_size) if v.memory_size else "Not specified"),
        ("Storage", lambda v: v.storage or "Not specified"),
        ("Storage Type", lambda v: v.storage_type or "Not specified"),
        ("Storage Size (GB)", lambda v: str(v.storage_size) if v.storage_size else "Not specified"),
        ("Display", lambda v: v.display or "Not specified"),
        ("Display Size", lambda v: f"{v.display_size}\"" if v.display_size else "Not specified"),
        ("Graphics", lambda v: v.graphics or "Not specified"),
        ("Price", lambda v: f"${v.price}" if v.price else "Not available"),
        ("Availability", lambda v: v.availability or "Unknown"),
        ("SKU", lambda v: v.variant_sku)
    ]

    # Add feature comparisons
    feature_keys = set()
    for variant in variants:
        if variant.additional_features:
            feature_keys.update(variant.additional_features.keys())

    for feature_key in sorted(feature_keys):
        feature_name = feature_key.replace('has_', '').replace('_', ' ').title()
        attributes.append((
            feature_name,
            lambda v, key=feature_key: "Yes" if v.additional_features.get(key) else "No"
        ))

    # Build matrix
    for attr_name, attr_func in attributes:
        matrix[attr_name] = [attr_func(variant) for variant in variants]

    return matrix


def _identify_differences(variants: List[Variant]) -> List[str]:
    """Identify key differences between variants"""
    differences = []

    # Price differences
    prices = [v.price for v in variants if v.price]
    if len(prices) > 1:
        min_price = min(prices)
        max_price = max(prices)
        price_diff = max_price - min_price
        if price_diff > 100:  # Significant price difference
            differences.append(f"Price range: ${min_price} - ${max_price} (${price_diff} difference)")

    # Brand differences
    brands = list(set(v.product.brand for v in variants))
    if len(brands) > 1:
        differences.append(f"Brands: {', '.join(brands)}")

    # Memory differences
    memory_sizes = list(set(v.memory_size for v in variants if v.memory_size))
    if len(memory_sizes) > 1:
        memory_sizes.sort()
        differences.append(f"Memory options: {', '.join(f'{m}GB' for m in memory_sizes)}")

    # Storage differences
    storage_types = list(set(v.storage_type for v in variants if v.storage_type))
    if len(storage_types) > 1:
        differences.append(f"Storage types: {', '.join(storage_types)}")

    storage_sizes = list(set(v.storage_size for v in variants if v.storage_size))
    if len(storage_sizes) > 1:
        storage_sizes.sort()
        differences.append(f"Storage sizes: {', '.join(f'{s}GB' for s in storage_sizes)}")

    # Processor differences
    processor_families = list(set(v.processor_family for v in variants if v.processor_family))
    if len(processor_families) > 1:
        differences.append(f"Processor families: {', '.join(processor_families)}")

    # Feature differences
    all_features = set()
    for variant in variants:
        if variant.additional_features:
            all_features.update(variant.additional_features.keys())

    differing_features = []
    for feature in all_features:
        feature_values = set()
        for variant in variants:
            feature_values.add(variant.additional_features.get(feature, False))

        if len(feature_values) > 1:  # Not all variants have the same value
            feature_name = feature.replace('has_', '').replace('_', ' ').title()
            differing_features.append(feature_name)

    if differing_features:
        differences.append(f"Feature differences: {', '.join(differing_features)}")

    return differences


def _get_comparison_reason(base_variant: Variant, comparison_variant: Variant) -> str:
    """Get reason why this variant is suggested for comparison"""
    reasons = []

    # Different brand
    if base_variant.product.brand != comparison_variant.product.brand:
        reasons.append(f"Different brand ({comparison_variant.product.brand})")

    # Similar price
    if base_variant.price and comparison_variant.price:
        price_diff_percent = abs(base_variant.price - comparison_variant.price) / base_variant.price * 100
        if price_diff_percent < 15:
            reasons.append("Similar price range")

    # Different specs
    if base_variant.memory_size != comparison_variant.memory_size:
        if comparison_variant.memory_size and base_variant.memory_size:
            if comparison_variant.memory_size > base_variant.memory_size:
                reasons.append("More memory")
            else:
                reasons.append("Less memory")

    if base_variant.storage_type != comparison_variant.storage_type:
        reasons.append(f"Different storage ({comparison_variant.storage_type})")

    if not reasons:
        reasons.append("Alternative option")

    return ", ".join(reasons)