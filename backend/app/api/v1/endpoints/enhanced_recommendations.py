"""
Enhanced recommendations endpoints with constraints and rationale
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.schemas.recommendations import (
    RecommendationRequest, RecommendationResponse,
    ComparisonRecommendation, SmartRecommendation
)
from app.services.enhanced_recommendations import EnhancedRecommendationService

router = APIRouter()


@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations based on detailed constraints"""
    service = EnhancedRecommendationService(db)

    try:
        recommendations = service.get_recommendations(
            request=request,
            user_id=str(current_user.id)
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/recommendations/compare", response_model=ComparisonRecommendation)
async def compare_products_with_recommendation(
    product_ids: List[str],
    comparison_aspects: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare multiple products and get recommendation"""
    if len(product_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 products required for comparison"
        )

    if len(product_ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 products allowed for comparison"
        )

    service = EnhancedRecommendationService(db)

    try:
        comparison = service.compare_products(
            product_ids=product_ids,
            comparison_aspects=comparison_aspects
        )
        return comparison
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing products: {str(e)}"
        )


@router.get("/recommendations/smart", response_model=List[SmartRecommendation])
async def get_smart_recommendations(
    recommendation_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get curated smart recommendations"""
    service = EnhancedRecommendationService(db)

    valid_types = ["budget_best", "performance_best", "value_best"]
    if recommendation_type and recommendation_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid recommendation type. Must be one of: {valid_types}"
        )

    try:
        recommendations = service.get_smart_recommendations(
            recommendation_type=recommendation_type or "all"
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting smart recommendations: {str(e)}"
        )


@router.get("/recommendations/personalized")
async def get_personalized_recommendations(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations based on user history"""
    from app.crud.enhanced_crud import UserRecommendationCRUD, UserPreferenceCRUD

    # Get user preferences
    user_prefs = UserPreferenceCRUD.get_by_user(db, str(current_user.id))

    # Get active recommendations
    recommendations = UserRecommendationCRUD.get_active_by_user(
        db, str(current_user.id), limit
    )

    return {
        "user_id": str(current_user.id),
        "recommendations": recommendations,
        "based_on": {
            "preferences": user_prefs.preferences if user_prefs else {},
            "viewed_products": user_prefs.viewed_products if user_prefs else [],
            "total_recommendations": len(recommendations)
        }
    }


@router.post("/recommendations/feedback")
async def record_recommendation_feedback(
    recommendation_id: str,
    action: str,  # "shown", "clicked", "dismissed"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record user interaction with recommendations"""
    from app.crud.enhanced_crud import UserRecommendationCRUD

    if action not in ["shown", "clicked", "dismissed"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be one of: shown, clicked, dismissed"
        )

    if action == "shown":
        UserRecommendationCRUD.mark_shown(db, recommendation_id)
    elif action == "clicked":
        UserRecommendationCRUD.mark_clicked(db, recommendation_id)

    return {"message": f"Recommendation {action} recorded"}


@router.get("/recommendations/requirements/suggest")
async def suggest_requirements_based_on_use_case(
    use_case: str,
    budget_max: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Suggest requirements based on use case"""
    use_case_suggestions = {
        "business": {
            "must_have_features": ["fingerprint reader", "backlit keyboard"],
            "nice_to_have_features": ["touchscreen"],
            "min_memory_gb": 16,
            "min_storage_gb": 256,
            "processor_preference": "Intel",
            "brands": ["HP", "Lenovo"],
            "min_rating": 4.0
        },
        "programming": {
            "must_have_features": ["backlit keyboard"],
            "nice_to_have_features": ["touchscreen", "fingerprint reader"],
            "min_memory_gb": 16,
            "min_storage_gb": 512,
            "processor_preference": "Intel",
            "brands": ["HP", "Lenovo"],
            "min_rating": 4.0
        },
        "gaming": {
            "must_have_features": [],
            "nice_to_have_features": ["backlit keyboard"],
            "min_memory_gb": 16,
            "min_storage_gb": 512,
            "processor_preference": "Intel",
            "brands": ["HP", "Lenovo"],
            "min_rating": 3.8
        },
        "student": {
            "must_have_features": [],
            "nice_to_have_features": ["touchscreen", "backlit keyboard"],
            "min_memory_gb": 8,
            "min_storage_gb": 256,
            "brands": ["HP", "Lenovo"],
            "min_rating": 4.0
        },
        "travel": {
            "must_have_features": [],
            "nice_to_have_features": ["touchscreen", "fingerprint reader"],
            "min_memory_gb": 8,
            "min_storage_gb": 256,
            "display_size_preference": "14\"",
            "brands": ["HP", "Lenovo"],
            "min_rating": 4.2
        }
    }

    use_case_lower = use_case.lower()
    suggestions = use_case_suggestions.get(use_case_lower)

    if not suggestions:
        # Return generic suggestions
        suggestions = {
            "must_have_features": [],
            "nice_to_have_features": ["backlit keyboard"],
            "min_memory_gb": 8,
            "min_storage_gb": 256,
            "brands": ["HP", "Lenovo"],
            "min_rating": 4.0
        }

    # Apply budget constraints
    if budget_max:
        suggestions["budget_max"] = budget_max
        if budget_max < 1000:
            suggestions["min_memory_gb"] = 8
            suggestions["min_storage_gb"] = 256
        elif budget_max < 1500:
            suggestions["min_memory_gb"] = 16
            suggestions["min_storage_gb"] = 512

    return {
        "use_case": use_case,
        "suggested_constraints": suggestions,
        "explanation": f"These constraints are optimized for {use_case} use cases based on typical requirements"
    }