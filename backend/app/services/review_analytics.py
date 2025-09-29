"""
Review Analytics Service - Provides insights and analysis for product reviews
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from decimal import Decimal
import json
import logging

from app.models import (
    Product, ReviewSummary, ReviewTheme, ReviewAnalytics,
    ProductQA, User
)
from app.schemas.review_analytics import (
    ReviewInsights, ReviewTrendAnalysis, ReviewThemeResponse,
    ReviewAnalyticsResponse
)

logger = logging.getLogger(__name__)


class ReviewAnalyticsService:
    """Service for analyzing and extracting insights from product reviews"""

    def __init__(self, db: Session):
        self.db = db

    def get_review_insights(self, product_id: str) -> ReviewInsights:
        """Get comprehensive review insights for a product"""

        # Get product and review summary
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        review_summary = product.review_summary

        # Get review themes
        themes = self.db.query(ReviewTheme).filter(
            ReviewTheme.product_id == product_id
        ).order_by(desc(ReviewTheme.mention_count)).all()

        # Get latest analytics
        latest_analytics = self.db.query(ReviewAnalytics).filter(
            ReviewAnalytics.product_id == product_id
        ).order_by(desc(ReviewAnalytics.created_at)).first()

        # Calculate sentiment distribution
        sentiment_distribution = self._calculate_sentiment_distribution(themes)

        # Extract top pros and cons
        top_pros = self._extract_top_aspects(themes, "positive", 5)
        top_cons = self._extract_top_aspects(themes, "negative", 5)

        # Generate key insights
        key_insights = self._generate_key_insights(
            review_summary, themes, latest_analytics
        )

        # Determine rating trend
        rating_trend = self._analyze_rating_trend(product_id)

        return ReviewInsights(
            product_id=product_id,
            total_reviews=review_summary.total_reviews if review_summary else 0,
            average_rating=review_summary.average_rating if review_summary else None,
            rating_trend=rating_trend,
            themes=[ReviewThemeResponse.from_orm(theme) for theme in themes[:10]],
            sentiment_summary=sentiment_distribution,
            top_pros=top_pros,
            top_cons=top_cons,
            recommended_for=latest_analytics.recommended_for if latest_analytics else [],
            not_recommended_for=latest_analytics.not_recommended_for if latest_analytics else [],
            key_insights=key_insights
        )

    def analyze_review_trends(
        self,
        product_id: str,
        period: str = "monthly",
        days_back: int = 90
    ) -> ReviewTrendAnalysis:
        """Analyze review trends over time"""

        # Get historical analytics data
        start_date = datetime.utcnow() - timedelta(days=days_back)

        analytics = self.db.query(ReviewAnalytics).filter(
            ReviewAnalytics.product_id == product_id,
            ReviewAnalytics.period == period,
            ReviewAnalytics.period_date >= start_date
        ).order_by(ReviewAnalytics.period_date).all()

        if not analytics:
            return ReviewTrendAnalysis(
                product_id=product_id,
                period=period,
                trend_data=[],
                rating_trend="stable",
                volume_trend="stable",
                sentiment_shift={}
            )

        # Build trend data
        trend_data = []
        for record in analytics:
            trend_data.append({
                "date": record.period_date.isoformat(),
                "total_reviews": record.total_reviews,
                "average_rating": float(record.average_rating) if record.average_rating else 0,
                "sentiment": record.sentiment_distribution
            })

        # Analyze trends
        rating_trend = self._determine_trend(
            [d["average_rating"] for d in trend_data]
        )
        volume_trend = self._determine_trend(
            [d["total_reviews"] for d in trend_data]
        )

        # Calculate sentiment shift
        sentiment_shift = self._calculate_sentiment_shift(analytics)

        return ReviewTrendAnalysis(
            product_id=product_id,
            period=period,
            trend_data=trend_data,
            rating_trend=rating_trend,
            volume_trend=volume_trend,
            sentiment_shift=sentiment_shift
        )

    def extract_review_themes(self, product_id: str) -> List[ReviewTheme]:
        """Extract and analyze themes from product reviews"""

        # This would typically use NLP/ML to extract themes
        # For now, we'll return existing themes or generate sample ones

        existing_themes = self.db.query(ReviewTheme).filter(
            ReviewTheme.product_id == product_id
        ).all()

        if existing_themes:
            return existing_themes

        # Generate sample themes (in production, use NLP)
        sample_themes = self._generate_sample_themes(product_id)

        for theme_data in sample_themes:
            theme = ReviewTheme(
                product_id=product_id,
                **theme_data
            )
            self.db.add(theme)

        self.db.commit()

        return self.db.query(ReviewTheme).filter(
            ReviewTheme.product_id == product_id
        ).all()

    def update_review_analytics(
        self,
        product_id: str,
        period: str = "daily"
    ) -> ReviewAnalytics:
        """Update review analytics for a product"""

        # Get current review data
        review_summary = self.db.query(ReviewSummary).filter(
            ReviewSummary.product_id == product_id
        ).first()

        if not review_summary:
            return None

        # Get themes for analysis
        themes = self.db.query(ReviewTheme).filter(
            ReviewTheme.product_id == product_id
        ).all()

        # Calculate analytics
        sentiment_dist = self._calculate_sentiment_distribution(themes)
        top_pros = self._extract_top_aspects(themes, "positive", 5)
        top_cons = self._extract_top_aspects(themes, "negative", 5)

        # Determine recommendations
        recommended_for = self._determine_recommended_for(themes, top_pros)
        not_recommended_for = self._determine_not_recommended_for(themes, top_cons)

        # Create or update analytics record
        analytics = ReviewAnalytics(
            product_id=product_id,
            period=period,
            period_date=datetime.utcnow().date(),
            total_reviews=review_summary.total_reviews,
            average_rating=review_summary.average_rating,
            rating_distribution=review_summary.rating_distribution,
            sentiment_distribution=sentiment_dist,
            top_pros=top_pros,
            top_cons=top_cons,
            recommended_for=recommended_for,
            not_recommended_for=not_recommended_for
        )

        self.db.add(analytics)
        self.db.commit()

        return analytics

    def get_comparative_review_analysis(
        self,
        product_ids: List[str]
    ) -> Dict[str, Any]:
        """Compare review analytics across multiple products"""

        comparison = {}

        for product_id in product_ids:
            insights = self.get_review_insights(product_id)
            if insights:
                comparison[product_id] = {
                    "average_rating": insights.average_rating,
                    "total_reviews": insights.total_reviews,
                    "sentiment": insights.sentiment_summary,
                    "top_pros": insights.top_pros[:3],
                    "top_cons": insights.top_cons[:3],
                    "rating_trend": insights.rating_trend
                }

        # Add comparative insights
        if len(comparison) > 1:
            comparison["insights"] = self._generate_comparative_insights(comparison)

        return comparison

    # Private helper methods

    def _calculate_sentiment_distribution(
        self,
        themes: List[ReviewTheme]
    ) -> Dict[str, float]:
        """Calculate sentiment distribution from themes"""

        if not themes:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_mentions = 0

        for theme in themes:
            if theme.sentiment in sentiment_counts:
                sentiment_counts[theme.sentiment] += theme.mention_count
                total_mentions += theme.mention_count

        if total_mentions == 0:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        return {
            sentiment: round(count / total_mentions * 100, 1)
            for sentiment, count in sentiment_counts.items()
        }

    def _extract_top_aspects(
        self,
        themes: List[ReviewTheme],
        sentiment: str,
        limit: int = 5
    ) -> List[str]:
        """Extract top aspects by sentiment"""

        filtered_themes = [
            theme for theme in themes
            if theme.sentiment == sentiment
        ]

        sorted_themes = sorted(
            filtered_themes,
            key=lambda x: x.mention_count,
            reverse=True
        )

        return [theme.theme for theme in sorted_themes[:limit]]

    def _generate_key_insights(
        self,
        review_summary: ReviewSummary,
        themes: List[ReviewTheme],
        analytics: ReviewAnalytics
    ) -> List[str]:
        """Generate key insights from review data"""

        insights = []

        if review_summary and review_summary.average_rating:
            if review_summary.average_rating >= 4.5:
                insights.append("Exceptionally well-rated product with strong customer satisfaction")
            elif review_summary.average_rating >= 4.0:
                insights.append("Well-received product with positive customer feedback")
            elif review_summary.average_rating < 3.5:
                insights.append("Mixed reviews suggest room for improvement")

        # Theme-based insights
        positive_themes = [t for t in themes if t.sentiment == "positive"]
        negative_themes = [t for t in themes if t.sentiment == "negative"]

        if positive_themes:
            top_positive = positive_themes[0].theme if positive_themes else None
            if top_positive:
                insights.append(f"Customers particularly appreciate: {top_positive}")

        if negative_themes:
            top_negative = negative_themes[0].theme if negative_themes else None
            if top_negative:
                insights.append(f"Common concern: {top_negative}")

        return insights

    def _analyze_rating_trend(self, product_id: str) -> str:
        """Analyze rating trend over recent period"""

        # Get recent analytics
        recent = self.db.query(ReviewAnalytics).filter(
            ReviewAnalytics.product_id == product_id
        ).order_by(desc(ReviewAnalytics.period_date)).limit(5).all()

        if len(recent) < 2:
            return "stable"

        ratings = [float(r.average_rating) for r in recent if r.average_rating]

        if not ratings:
            return "stable"

        return self._determine_trend(ratings)

    def _determine_trend(self, values: List[float]) -> str:
        """Determine trend from a list of values"""

        if len(values) < 2:
            return "stable"

        # Simple linear trend analysis
        avg_first_half = sum(values[:len(values)//2]) / (len(values)//2)
        avg_second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

        change_percent = ((avg_second_half - avg_first_half) / avg_first_half) * 100

        if change_percent > 5:
            return "improving"
        elif change_percent < -5:
            return "declining"
        else:
            return "stable"

    def _calculate_sentiment_shift(
        self,
        analytics: List[ReviewAnalytics]
    ) -> Dict[str, float]:
        """Calculate sentiment shift over time"""

        if len(analytics) < 2:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        first = analytics[0].sentiment_distribution or {}
        last = analytics[-1].sentiment_distribution or {}

        shift = {}
        for sentiment in ["positive", "negative", "neutral"]:
            first_val = first.get(sentiment, 0)
            last_val = last.get(sentiment, 0)
            shift[sentiment] = round(last_val - first_val, 1)

        return shift

    def _generate_sample_themes(self, product_id: str) -> List[Dict]:
        """Generate sample themes for demonstration"""

        return [
            {
                "theme": "Battery Life",
                "aspect": "battery",
                "sentiment": "positive",
                "confidence": 0.85,
                "mention_count": 45,
                "example_quotes": ["Great battery life", "Lasts all day"]
            },
            {
                "theme": "Build Quality",
                "aspect": "build_quality",
                "sentiment": "positive",
                "confidence": 0.90,
                "mention_count": 38,
                "example_quotes": ["Solid construction", "Feels premium"]
            },
            {
                "theme": "Performance",
                "aspect": "performance",
                "sentiment": "positive",
                "confidence": 0.88,
                "mention_count": 52,
                "example_quotes": ["Fast processor", "Handles multitasking well"]
            },
            {
                "theme": "Display Quality",
                "aspect": "display",
                "sentiment": "negative",
                "confidence": 0.75,
                "mention_count": 12,
                "example_quotes": ["Screen could be brighter", "Average display"]
            }
        ]

    def _determine_recommended_for(
        self,
        themes: List[ReviewTheme],
        top_pros: List[str]
    ) -> List[str]:
        """Determine who the product is recommended for"""

        recommendations = []

        # Analyze themes and pros to determine recommendations
        theme_keywords = {
            "battery": ["travelers", "mobile workers"],
            "performance": ["power users", "professionals"],
            "build_quality": ["business users", "long-term investment"],
            "keyboard": ["writers", "programmers"],
            "portability": ["students", "commuters"]
        }

        for theme in themes:
            if theme.sentiment == "positive":
                for keyword, audiences in theme_keywords.items():
                    if keyword in theme.aspect.lower():
                        recommendations.extend(audiences)

        return list(set(recommendations))[:5]

    def _determine_not_recommended_for(
        self,
        themes: List[ReviewTheme],
        top_cons: List[str]
    ) -> List[str]:
        """Determine who the product is not recommended for"""

        not_recommended = []

        # Analyze themes and cons
        con_keywords = {
            "display": ["graphic designers", "video editors"],
            "graphics": ["gamers", "3D modelers"],
            "weight": ["frequent travelers"],
            "battery": ["heavy users without power access"]
        }

        for theme in themes:
            if theme.sentiment == "negative":
                for keyword, audiences in con_keywords.items():
                    if keyword in theme.aspect.lower():
                        not_recommended.extend(audiences)

        return list(set(not_recommended))[:3]

    def _generate_comparative_insights(
        self,
        comparison: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from product comparison"""

        insights = []

        # Find best rated
        best_rated = max(
            comparison.items(),
            key=lambda x: x[1].get("average_rating", 0) if isinstance(x[1], dict) else 0
        )

        if best_rated and best_rated[0] != "insights":
            insights.append(f"Highest rated: {best_rated[0]}")

        # Find most reviewed
        most_reviewed = max(
            comparison.items(),
            key=lambda x: x[1].get("total_reviews", 0) if isinstance(x[1], dict) else 0
        )

        if most_reviewed and most_reviewed[0] != "insights":
            insights.append(f"Most reviewed: {most_reviewed[0]}")

        return insights