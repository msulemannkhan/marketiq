from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchFilters, FilterOptions, AutoCompleteResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search products with filters and sorting"""
    search_service = SearchService(db)

    # Perform search
    results = await search_service.search(
        query=request.query,
        filters=request.filters,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        limit=request.limit,
        offset=request.offset
    )

    # Get total count for pagination
    # Note: In production, this could be optimized with a separate count query
    total_results = await search_service.search(
        query=request.query,
        filters=request.filters,
        limit=1000,  # Large number to get total count
        offset=0
    )

    # Get search suggestions
    suggestions = []
    if request.query:
        suggestions = await search_service.get_suggestions(request.query)

    return SearchResponse(
        results=results,
        total=len(total_results),
        filters_applied=request.filters.dict(exclude_none=True) if request.filters else {},
        query=request.query,
        suggestions=suggestions
    )


@router.get("/search/filters", response_model=FilterOptions)
async def get_filter_options(db: Session = Depends(get_db)):
    """Get available filter options based on current catalog"""
    search_service = SearchService(db)
    filter_options = await search_service.get_filter_options()

    return FilterOptions(
        brands=filter_options["brands"],
        processor_families=filter_options["processor_families"],
        memory_sizes=filter_options["memory_sizes"],
        storage_types=filter_options["storage_types"],
        price_range=filter_options["price_range"],
        display_sizes=[]  # Could be added if needed
    )


@router.get("/search/suggestions", response_model=AutoCompleteResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions to return"),
    db: Session = Depends(get_db)
):
    """Get search auto-complete suggestions"""
    search_service = SearchService(db)

    suggestions = await search_service.get_suggestions(q, limit)

    # Categorize suggestions (basic implementation)
    categories = {
        "products": [],
        "brands": [],
        "features": []
    }

    # Define categorization keywords
    brand_keywords = ['hp', 'lenovo', 'dell']
    feature_keywords = ['touchscreen', 'gaming', 'business', 'ultrabook', 'convertible', 'lightweight', 'portable', 'inch laptops', 'ram laptops', 'ssd laptops']
    processor_keywords = ['intel', 'amd', 'ryzen', 'core', 'processor']

    for suggestion in suggestions:
        suggestion_lower = suggestion.lower()

        # Check if it's a standalone brand name or starts with brand
        if (suggestion_lower in brand_keywords or
            any(suggestion_lower.startswith(brand) for brand in brand_keywords) or
            any(f"{brand} " in suggestion_lower for brand in ['hp', 'lenovo', 'dell'])):
            categories["brands"].append(suggestion)
        # Check if it's a feature-related term
        elif any(feature in suggestion_lower for feature in feature_keywords):
            categories["features"].append(suggestion)
        # Check if it's processor-related
        elif any(proc in suggestion_lower for proc in processor_keywords):
            categories["products"].append(suggestion)  # Treat processor suggestions as product specs
        # Everything else is considered a product
        else:
            categories["products"].append(suggestion)

    return AutoCompleteResponse(
        suggestions=suggestions,
        categories=categories
    )


@router.get("/search/quick")
async def quick_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Quick search endpoint for instant results"""
    search_service = SearchService(db)

    # Perform simplified search
    results = await search_service.search(
        query=q,
        filters=None,
        sort_by="price",
        sort_order="asc",
        limit=limit,
        offset=0
    )

    # Return simplified response for quick results
    quick_results = []
    for result in results:
        quick_results.append({
            "id": result.variant.id,
            "name": result.variant.product_name,
            "brand": result.variant.brand,
            "price": result.variant.price,
            "processor": result.variant.processor,
            "memory": result.variant.memory,
            "relevance_score": result.relevance_score
        })

    return {
        "results": quick_results,
        "total": len(quick_results),
        "query": q
    }


@router.post("/search/advanced")
async def advanced_search(
    query: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    processor_family: Optional[str] = None,
    min_memory: Optional[int] = None,
    storage_type: Optional[str] = None,
    min_storage_size: Optional[int] = None,
    sort_by: str = "price",
    sort_order: str = "asc",
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Advanced search with individual filter parameters"""

    # Create filters object
    filters = SearchFilters(
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        processor_family=processor_family,
        min_memory=min_memory,
        storage_type=storage_type,
        min_storage_size=min_storage_size
    )

    # Create search request
    search_request = SearchRequest(
        query=query,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    # Use the main search endpoint
    return await search_products(search_request, db)


@router.post("/search/semantic")
async def semantic_search(
    query: str = Query(..., min_length=3, description="Natural language search query"),
    limit: int = Query(10, ge=1, le=50),
    include_similar: bool = Query(True, description="Include semantically similar products"),
    db: Session = Depends(get_db)
):
    """Semantic search using natural language processing"""
    search_service = SearchService(db)

    try:
        results = await search_service.semantic_search(
            query=query,
            limit=limit,
            include_similar=include_similar
        )

        return {
            "results": results,
            "total": len(results),
            "query": query,
            "search_type": "semantic",
            "intent_analysis": await search_service.analyze_search_intent(query)
        }
    except Exception as e:
        return {"error": f"Semantic search failed: {str(e)}", "fallback_results": []}


@router.get("/search/intelligent")
async def intelligent_search(
    q: str = Query(..., min_length=2, description="Search query"),
    user_context: Optional[str] = Query(None, description="User context or preferences"),
    budget_range: Optional[str] = Query(None, description="Budget range like '800-1200'"),
    use_case: Optional[str] = Query(None, description="Intended use case"),
    limit: int = Query(10, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Intelligent search with context awareness and smart filtering"""
    search_service = SearchService(db)

    try:
        # Parse budget range if provided
        budget_min, budget_max = None, None
        if budget_range and '-' in budget_range:
            try:
                budget_parts = budget_range.split('-')
                budget_min = float(budget_parts[0])
                budget_max = float(budget_parts[1])
            except:
                pass

        results = await search_service.intelligent_search(
            query=q,
            user_context=user_context,
            budget_min=budget_min,
            budget_max=budget_max,
            use_case=use_case,
            limit=limit
        )

        return {
            "results": results,
            "query": q,
            "intelligent_insights": await search_service.get_search_insights(q, results),
            "recommendations": await search_service.get_related_searches(q)
        }
    except Exception as e:
        return {"error": f"Intelligent search failed: {str(e)}", "results": []}


@router.get("/search/trending")
async def get_trending_searches(
    period: str = Query("7d", regex="^(1d|7d|30d)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending search queries and popular products"""
    search_service = SearchService(db)

    try:
        trending = await search_service.get_trending_searches(period, limit)

        return {
            "period": period,
            "trending_queries": trending.get("queries", []),
            "popular_products": trending.get("products", []),
            "search_patterns": trending.get("patterns", [])
        }
    except Exception as e:
        return {"error": f"Failed to fetch trending searches: {str(e)}", "trending_queries": []}


@router.post("/search/history")
async def save_search_history(
    query: str,
    filters_applied: Optional[dict] = None,
    results_count: int = 0,
    selected_product_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Save user search history for analytics and personalization"""
    search_service = SearchService(db)

    try:
        history_entry = await search_service.save_search_history(
            query=query,
            filters_applied=filters_applied or {},
            results_count=results_count,
            selected_product_id=selected_product_id
        )

        return {
            "success": True,
            "history_id": history_entry.get("id"),
            "message": "Search history saved"
        }
    except Exception as e:
        return {"error": f"Failed to save search history: {str(e)}", "success": False}








