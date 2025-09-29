from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.post("/recommendations")
async def get_recommendations(
    budget: Optional[float] = None,
    requirements: List[str] = [],
    preferences: List[str] = [],
    use_case: Optional[str] = None,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: Session = Depends(get_db)
):
    """Get personalized laptop recommendations"""

    recommendation_engine = RecommendationEngine(db)

    try:
        recommendations = await recommendation_engine.get_recommendations(
            budget=budget,
            requirements=requirements,
            preferences=preferences,
            use_case=use_case,
            limit=limit
        )

        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "criteria": {
                "budget": budget,
                "requirements": requirements,
                "preferences": preferences,
                "use_case": use_case
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/recommendations/quick")
async def get_quick_recommendations(
    budget: Optional[float] = Query(None, description="Maximum budget"),
    use_case: str = Query("business", description="Use case: business, gaming, programming, travel"),
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get quick recommendations based on budget and use case"""

    recommendation_engine = RecommendationEngine(db)

    # Define common requirements based on use case
    use_case_requirements = {
        "business": ["8gb ram", "ssd", "fingerprint"],
        "programming": ["16gb ram", "ssd", "fast processor"],
        "gaming": ["16gb ram", "dedicated graphics", "fast processor"],
        "travel": ["lightweight", "battery life", "14 inch"],
        "office": ["8gb ram", "ssd"],
        "student": ["budget friendly", "basic features"]
    }

    requirements = use_case_requirements.get(use_case.lower(), [])

    recommendations = await recommendation_engine.get_recommendations(
        budget=budget,
        requirements=requirements,
        use_case=use_case,
        limit=limit
    )

    return {
        "recommendations": recommendations,
        "use_case": use_case,
        "budget": budget,
        "auto_requirements": requirements
    }


@router.get("/recommendations/trending")
async def get_trending_recommendations(
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get trending/popular laptop recommendations"""

    recommendation_engine = RecommendationEngine(db)

    # Get recommendations based on popular configurations
    # This is a simplified version - in production, this might be based on actual sales/view data
    popular_preferences = [
        "good value",
        "business use",
        "reliable"
    ]

    recommendations = await recommendation_engine.get_recommendations(
        budget=1500,  # Popular price point
        preferences=popular_preferences,
        use_case="business",
        limit=limit
    )

    return {
        "trending_recommendations": recommendations,
        "note": "Based on popular configurations and price points"
    }


@router.get("/recommendations/budget-tiers")
async def get_budget_tier_recommendations(db: Session = Depends(get_db)):
    """Get recommendations across different budget tiers"""

    recommendation_engine = RecommendationEngine(db)

    budget_tiers = [
        {"name": "Budget", "max_budget": 800, "description": "Essential features for basic use"},
        {"name": "Mid-Range", "max_budget": 1200, "description": "Balanced performance and features"},
        {"name": "Premium", "max_budget": 1800, "description": "High-end specifications and features"},
        {"name": "Enterprise", "max_budget": 2500, "description": "Top-tier business laptops"}
    ]

    tier_recommendations = []

    for tier in budget_tiers:
        recommendations = await recommendation_engine.get_recommendations(
            budget=tier["max_budget"],
            use_case="business",
            limit=2
        )

        tier_recommendations.append({
            "tier": tier["name"],
            "budget_range": f"Up to ${tier['max_budget']}",
            "description": tier["description"],
            "recommendations": recommendations
        })

    return {
        "budget_tiers": tier_recommendations,
        "note": "Recommendations optimized for different budget ranges"
    }


@router.post("/recommendations/custom")
async def get_custom_recommendations(
    processor_preference: Optional[str] = None,  # "intel", "amd"
    min_memory: Optional[int] = None,
    min_storage: Optional[int] = None,
    storage_type_preference: Optional[str] = None,  # "ssd", "nvme"
    max_weight: Optional[str] = None,  # "lightweight", "standard"
    security_features: bool = False,
    touchscreen: bool = False,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    brand_preference: Optional[str] = None,
    limit: int = Query(5, ge=1, le=15),
    db: Session = Depends(get_db)
):
    """Get custom recommendations based on detailed preferences"""

    recommendation_engine = RecommendationEngine(db)

    # Build requirements and preferences from parameters
    requirements = []
    preferences = []

    if min_memory:
        requirements.append(f"{min_memory}gb ram")

    if min_storage:
        requirements.append(f"{min_storage}gb storage")

    if storage_type_preference:
        requirements.append(storage_type_preference)

    if security_features:
        requirements.append("fingerprint")

    if touchscreen:
        requirements.append("touchscreen")

    if processor_preference:
        preferences.append(processor_preference)

    if max_weight == "lightweight":
        preferences.append("lightweight")

    if brand_preference:
        preferences.append(f"{brand_preference} brand")

    # Use average of budget range if both provided
    budget = None
    if budget_min and budget_max:
        budget = (budget_min + budget_max) / 2
    elif budget_max:
        budget = budget_max

    recommendations = await recommendation_engine.get_recommendations(
        budget=budget,
        requirements=requirements,
        preferences=preferences,
        limit=limit
    )

    return {
        "custom_recommendations": recommendations,
        "applied_criteria": {
            "requirements": requirements,
            "preferences": preferences,
            "budget_range": f"${budget_min or 0} - ${budget_max or 'unlimited'}",
            "processor_preference": processor_preference,
            "brand_preference": brand_preference
        }
    }