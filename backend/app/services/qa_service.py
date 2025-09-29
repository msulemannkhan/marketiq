"""
Product Q&A Service
Handles question and answer management for products
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime
from uuid import UUID

from app.models.product_qa import ProductQuestion, ProductAnswer
from app.schemas.product_qa import QuestionCreate, AnswerCreate, QuestionResponse, AnswerResponse


class QAService:

    @staticmethod
    def get_product_questions(product_id: int, db: Session, limit: int = 50) -> List[QuestionResponse]:
        """Get questions for a product with answers"""
        questions = db.query(ProductQuestion).filter(
            ProductQuestion.product_id == product_id,
            ProductQuestion.is_active == True
        ).order_by(desc(ProductQuestion.created_at)).limit(limit).all()

        result = []
        for question in questions:
            answers = db.query(ProductAnswer).filter(
                ProductAnswer.question_id == question.id,
                ProductAnswer.is_active == True
            ).order_by(desc(ProductAnswer.helpful_count)).all()

            result.append(QuestionResponse(
                id=question.id,
                product_id=question.product_id,
                user_id=question.user_id,
                question_text=question.question_text,
                category=question.category,
                helpful_count=question.helpful_count,
                created_at=question.created_at,
                answers=[AnswerResponse(
                    id=answer.id,
                    question_id=answer.question_id,
                    user_id=answer.user_id,
                    answer_text=answer.answer_text,
                    is_verified=answer.is_verified,
                    helpful_count=answer.helpful_count,
                    created_at=answer.created_at
                ) for answer in answers]
            ))

        return result

    @staticmethod
    def create_question(question_data: QuestionCreate, user_id: UUID, db: Session) -> QuestionResponse:
        """Create a new question"""
        question = ProductQuestion(
            product_id=question_data.product_id,
            user_id=user_id,
            question_text=question_data.question_text,
            category=question_data.category or "general"
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        return QuestionResponse(
            id=question.id,
            product_id=question.product_id,
            user_id=question.user_id,
            question_text=question.question_text,
            category=question.category,
            helpful_count=question.helpful_count,
            created_at=question.created_at,
            answers=[]
        )

    @staticmethod
    def create_answer(answer_data: AnswerCreate, user_id: UUID, db: Session) -> AnswerResponse:
        """Create a new answer"""
        answer = ProductAnswer(
            question_id=answer_data.question_id,
            user_id=user_id,
            answer_text=answer_data.answer_text,
            is_verified=False  # Admin verification required
        )

        db.add(answer)
        db.commit()
        db.refresh(answer)

        return AnswerResponse(
            id=answer.id,
            question_id=answer.question_id,
            user_id=answer.user_id,
            answer_text=answer.answer_text,
            is_verified=answer.is_verified,
            helpful_count=answer.helpful_count,
            created_at=answer.created_at
        )

    @staticmethod
    def mark_helpful(item_type: str, item_id: UUID, db: Session) -> bool:
        """Mark question or answer as helpful"""
        if item_type == "question":
            item = db.query(ProductQuestion).filter(ProductQuestion.id == item_id).first()
        elif item_type == "answer":
            item = db.query(ProductAnswer).filter(ProductAnswer.id == item_id).first()
        else:
            return False

        if item:
            item.helpful_count += 1
            db.commit()
            return True
        return False

    @staticmethod
    def get_trending_questions(db: Session, limit: int = 10) -> List[Dict]:
        """Get trending questions across all products"""
        questions = db.query(ProductQuestion).filter(
            ProductQuestion.is_active == True
        ).order_by(desc(ProductQuestion.helpful_count)).limit(limit).all()

        return [
            {
                "id": q.id,
                "product_id": q.product_id,
                "question_text": q.question_text,
                "category": q.category,
                "helpful_count": q.helpful_count,
                "answer_count": db.query(ProductAnswer).filter(
                    ProductAnswer.question_id == q.id,
                    ProductAnswer.is_active == True
                ).count()
            }
            for q in questions
        ]

    @staticmethod
    def search_questions(query: str, product_id: Optional[int], db: Session) -> List[QuestionResponse]:
        """Search questions by text"""
        filters = [ProductQuestion.is_active == True]

        if product_id:
            filters.append(ProductQuestion.product_id == product_id)

        if query:
            filters.append(ProductQuestion.question_text.ilike(f"%{query}%"))

        questions = db.query(ProductQuestion).filter(*filters).limit(20).all()

        result = []
        for question in questions:
            answers = db.query(ProductAnswer).filter(
                ProductAnswer.question_id == question.id,
                ProductAnswer.is_active == True
            ).order_by(desc(ProductAnswer.helpful_count)).all()

            result.append(QuestionResponse(
                id=question.id,
                product_id=question.product_id,
                user_id=question.user_id,
                question_text=question.question_text,
                category=question.category,
                helpful_count=question.helpful_count,
                created_at=question.created_at,
                answers=[AnswerResponse(
                    id=answer.id,
                    question_id=answer.question_id,
                    user_id=answer.user_id,
                    answer_text=answer.answer_text,
                    is_verified=answer.is_verified,
                    helpful_count=answer.helpful_count,
                    created_at=answer.created_at
                ) for answer in answers]
            ))

        return result