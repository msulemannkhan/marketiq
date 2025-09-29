"""
Review Intelligence Service
Handles sentiment analysis, theme extraction, and review insights
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import Counter
import re

from app.models.review import ReviewSummary, Review
from app.models.review_theme import ReviewTheme, ReviewAnalytics
from app.schemas.review_analytics import ReviewInsights, ReviewTrendAnalysis


class ReviewIntelligenceService:

    @staticmethod
    def analyze_product_reviews(product_id: int, db: Session) -> ReviewInsights:
        """Comprehensive review analysis for a product"""
        reviews = db.query(ReviewSummary).filter(
            ReviewSummary.product_id == product_id
        ).all()

        if not reviews:
            return ReviewInsights(
                product_id=product_id,
                total_reviews=0,
                themes=[],
                sentiment_summary={},
                key_insights=["No reviews available for analysis"]
            )

        # Calculate basic metrics
        total_reviews = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total_reviews

        # Sentiment analysis
        sentiment_summary = ReviewIntelligenceService._analyze_sentiment(reviews)

        # Extract themes
        themes = ReviewIntelligenceService._extract_themes(reviews, db)

        # Generate insights
        pros, cons = ReviewIntelligenceService._extract_pros_cons(reviews)
        recommended_for = ReviewIntelligenceService._extract_use_cases(reviews, positive=True)
        key_insights = ReviewIntelligenceService._generate_insights(reviews, avg_rating, sentiment_summary)

        return ReviewInsights(
            product_id=product_id,
            total_reviews=total_reviews,
            average_rating=avg_rating,
            rating_trend=ReviewIntelligenceService._calculate_trend(reviews),
            themes=themes,
            sentiment_summary=sentiment_summary,
            top_pros=pros[:5],
            top_cons=cons[:5],
            recommended_for=recommended_for,
            key_insights=key_insights
        )

    @staticmethod
    def get_review_trends(product_id: int, period: str, db: Session) -> ReviewTrendAnalysis:
        """Get review trends over time"""
        days_map = {"weekly": 7, "monthly": 30, "quarterly": 90}
        days = days_map.get(period, 30)

        start_date = datetime.now() - timedelta(days=days)
        reviews = db.query(Review).filter(
            Review.product_id == product_id,
            Review.review_date >= start_date
        ).order_by(Review.review_date).all()

        trend_data = ReviewIntelligenceService._build_trend_data(reviews, period)
        rating_trend = ReviewIntelligenceService._calculate_trend(reviews)
        volume_trend = ReviewIntelligenceService._calculate_volume_trend(reviews)

        return ReviewTrendAnalysis(
            product_id=product_id,
            period=period,
            trend_data=trend_data,
            rating_trend=rating_trend,
            volume_trend=volume_trend,
            sentiment_shift=ReviewIntelligenceService._calculate_sentiment_shift(reviews)
        )

    @staticmethod
    def _analyze_sentiment(reviews: List[ReviewSummary]) -> Dict[str, float]:
        """Analyze sentiment distribution"""
        if not reviews:
            return {"positive": 0, "neutral": 0, "negative": 0}

        positive = sum(1 for r in reviews if r.rating >= 4)
        negative = sum(1 for r in reviews if r.rating <= 2)
        neutral = len(reviews) - positive - negative

        total = len(reviews)
        return {
            "positive": round(positive / total * 100, 1),
            "neutral": round(neutral / total * 100, 1),
            "negative": round(negative / total * 100, 1)
        }

    @staticmethod
    def _extract_themes(reviews: List[ReviewSummary], db: Session) -> List:
        """Extract common themes from reviews"""
        # This would use NLP in production, using simple keyword extraction for now
        common_themes = [
            "battery_life", "performance", "build_quality", "keyboard",
            "display", "price_value", "portability", "customer_service"
        ]

        theme_mentions = Counter()
        for review in reviews:
            content = review.content.lower()
            for theme in common_themes:
                if any(keyword in content for keyword in ReviewIntelligenceService._get_theme_keywords(theme)):
                    theme_mentions[theme] += 1

        # Return top themes with mock data structure
        return [
            {
                "theme": theme,
                "sentiment": "positive" if theme in ["performance", "build_quality"] else "mixed",
                "frequency": count,
                "impact_score": min(count / len(reviews), 1.0)
            }
            for theme, count in theme_mentions.most_common(5)
        ]

    @staticmethod
    def _get_theme_keywords(theme: str) -> List[str]:
        """Get keywords for theme detection"""
        keywords_map = {
            "battery_life": ["battery", "charge", "power", "lasted", "drain"],
            "performance": ["fast", "slow", "speed", "lag", "responsive", "performance"],
            "build_quality": ["solid", "sturdy", "cheap", "flimsy", "durable", "construction"],
            "keyboard": ["keyboard", "keys", "typing", "comfortable", "cramped"],
            "display": ["screen", "display", "bright", "dim", "resolution", "colors"],
            "price_value": ["price", "value", "expensive", "cheap", "worth", "cost"],
            "portability": ["light", "heavy", "portable", "weight", "travel"],
            "customer_service": ["support", "service", "help", "response", "staff"]
        }
        return keywords_map.get(theme, [])

    @staticmethod
    def _extract_pros_cons(reviews: List[ReviewSummary]) -> tuple:
        """Extract common pros and cons"""
        # Mock implementation - would use NLP in production
        pros = ["Great performance", "Excellent build quality", "Good value", "Fast startup", "Reliable"]
        cons = ["Battery could be better", "Slightly heavy", "Gets warm", "Limited ports", "Loud fan"]
        return pros, cons

    @staticmethod
    def _extract_use_cases(reviews: List[ReviewSummary], positive: bool = True) -> List[str]:
        """Extract recommended use cases"""
        # Mock implementation
        if positive:
            return ["Business use", "Programming", "Office work", "Web browsing", "Light gaming"]
        else:
            return ["Heavy gaming", "Video editing", "3D rendering"]

    @staticmethod
    def _generate_insights(reviews: List[ReviewSummary], avg_rating: float, sentiment: Dict) -> List[str]:
        """Generate key insights"""
        insights = []

        if avg_rating >= 4.0:
            insights.append(f"Highly rated with {avg_rating:.1f}/5 average")
        elif avg_rating <= 2.5:
            insights.append(f"Below average rating of {avg_rating:.1f}/5 needs attention")

        if sentiment["positive"] > 70:
            insights.append(f"{sentiment['positive']:.0f}% positive sentiment indicates strong customer satisfaction")

        if len(reviews) > 100:
            insights.append(f"Large sample size ({len(reviews)} reviews) provides reliable feedback")

        return insights[:3]  # Keep top 3 insights

    @staticmethod
    def _calculate_trend(reviews: List[Review]) -> str:
        """Calculate rating trend"""
        if len(reviews) < 10:
            return "stable"

        # Compare recent vs older reviews
        recent = reviews[-10:]
        older = reviews[:-10] if len(reviews) > 10 else reviews[:10]

        recent_avg = sum(r.rating for r in recent) / len(recent)
        older_avg = sum(r.rating for r in older) / len(older)

        diff = recent_avg - older_avg
        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        return "stable"

    @staticmethod
    def _calculate_volume_trend(reviews: List[Review]) -> str:
        """Calculate review volume trend"""
        if len(reviews) < 20:
            return "stable"

        # Compare recent vs older volume
        mid_point = len(reviews) // 2
        recent_count = len(reviews) - mid_point
        older_count = mid_point

        if recent_count > older_count * 1.2:
            return "increasing"
        elif recent_count < older_count * 0.8:
            return "decreasing"
        return "stable"

    @staticmethod
    def _build_trend_data(reviews: List[Review], period: str) -> List[Dict]:
        """Build time series trend data"""
        # Mock implementation - would aggregate by actual time periods
        return [
            {"date": "2024-01-01", "rating_avg": 4.2, "review_count": 15},
            {"date": "2024-01-15", "rating_avg": 4.1, "review_count": 12},
            {"date": "2024-02-01", "rating_avg": 4.3, "review_count": 18}
        ]

    @staticmethod
    def _calculate_sentiment_shift(reviews: List[Review]) -> Dict[str, float]:
        """Calculate sentiment changes over time"""
        if len(reviews) < 20:
            return {"positive_change": 0.0, "negative_change": 0.0}

        mid_point = len(reviews) // 2
        recent = reviews[mid_point:]
        older = reviews[:mid_point]

        recent_sentiment = ReviewIntelligenceService._analyze_sentiment(recent)
        older_sentiment = ReviewIntelligenceService._analyze_sentiment(older)

        return {
            "positive_change": recent_sentiment["positive"] - older_sentiment["positive"],
            "negative_change": recent_sentiment["negative"] - older_sentiment["negative"]
        }