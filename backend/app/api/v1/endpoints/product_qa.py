"""
Product Q&A endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.product_qa import ProductQA
from app.schemas import (
    ProductQACreate, ProductQAUpdate, ProductQAResponse, ProductQASummary, TrendingQuestionResponse
)
from app.crud.enhanced_crud import ProductQACRUD

router = APIRouter()


@router.get("/{product_id}/qa", response_model=List[ProductQAResponse])
async def get_product_qa(
    product_id: str,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Q&A for a specific product"""
    qa_items = ProductQACRUD.get_by_product(db, product_id, limit)
    return qa_items


@router.post("/{product_id}/qa", response_model=ProductQAResponse)
async def create_product_qa(
    product_id: str,
    qa_data: ProductQACreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new Q&A for a product"""
    qa_data.product_id = product_id
    qa_item = ProductQACRUD.create(db, qa_data)
    return qa_item


@router.put("/qa/{qa_id}", response_model=ProductQAResponse)
async def update_product_qa(
    qa_id: str,
    qa_update: ProductQAUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update Q&A item"""
    qa_item = ProductQACRUD.update(db, qa_id, qa_update)
    if not qa_item:
        raise HTTPException(status_code=404, detail="Q&A item not found")
    return qa_item


@router.delete("/qa/{qa_id}")
async def delete_product_qa(
    qa_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete Q&A item"""
    deleted = ProductQACRUD.delete(db, qa_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Q&A item not found")
    return {"message": "Q&A item deleted successfully"}


@router.get("/{product_id}/qa/summary", response_model=ProductQASummary)
async def get_qa_summary(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Q&A summary for a product"""
    all_qa = ProductQACRUD.get_by_product(db, product_id, limit=1000)

    total_questions = len(all_qa)
    verified_questions = len([qa for qa in all_qa if qa.verified])
    most_helpful = sorted(all_qa, key=lambda x: x.helpful_count, reverse=True)[:5]
    recent_questions = sorted(all_qa, key=lambda x: x.created_at, reverse=True)[:5]

    return ProductQASummary(
        total_questions=total_questions,
        verified_questions=verified_questions,
        most_helpful=most_helpful,
        recent_questions=recent_questions
    )


@router.get("/qa/trending", response_model=List[TrendingQuestionResponse])
async def get_trending_questions(
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Get trending questions across all products"""
    try:
        # Get most helpful QA across all products
        trending_qa = db.query(ProductQA).order_by(
            desc(ProductQA.helpful_count)
        ).limit(limit).all()

        return [
            TrendingQuestionResponse(
                id=qa.id,
                product_id=qa.product_id,
                question_text=qa.question,
                category="general",  # Default category as it's not in current model
                helpful_count=qa.helpful_count,
                answer_count=1 if qa.answer else 0
            )
            for qa in trending_qa
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending questions: {str(e)}")


@router.get("/qa/search", response_model=List[ProductQAResponse])
async def search_questions(
    q: str = Query(..., min_length=3),
    product_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search questions by text"""
    try:
        query = db.query(ProductQA)

        # Add product filter if specified
        if product_id:
            query = query.filter(ProductQA.product_id == product_id)

        # Add text search
        query = query.filter(
            or_(
                ProductQA.question.ilike(f"%{q}%"),
                ProductQA.answer.ilike(f"%{q}%")
            )
        )

        results = query.order_by(desc(ProductQA.helpful_count)).limit(20).all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/qa/{qa_id}/helpful")
async def mark_qa_helpful(
    qa_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a Q&A as helpful"""
    try:
        qa_item = db.query(ProductQA).filter(ProductQA.id == qa_id).first()
        if not qa_item:
            raise HTTPException(status_code=404, detail="Q&A not found")

        qa_item.helpful_count += 1
        db.commit()

        return {"success": True, "message": "Marked as helpful", "helpful_count": qa_item.helpful_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark helpful: {str(e)}")