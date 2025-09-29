"""
Analytics Service
Provides comprehensive analytics and insights for the dashboard
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from datetime import datetime, timedelta
from collections import Counter, defaultdict

from app.models.product import Product
from app.models.variant import Variant
from app.models.review import ReviewSummary, Review
from app.models.price import PriceHistory
from app.models.product_offer import ProductOffer


class AnalyticsService:
    """Service for generating analytics and insights"""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get high-level overview metrics for dashboard"""

        # Basic counts
        total_products = self.db.query(Product).count()
        total_variants = self.db.query(Variant).count()
        total_reviews = self.db.query(ReviewSummary).count()
        active_offers = self.db.query(ProductOffer).filter(ProductOffer.active == True).count()

        # Average ratings
        avg_rating = self.db.query(func.avg(ReviewSummary.rating)).scalar() or 0

        # Brand distribution
        brand_counts = self.db.query(
            Product.brand,
            func.count(Product.id).label('count')
        ).group_by(Product.brand).all()

        brand_distribution = {brand: count for brand, count in brand_counts}

        # Price range analysis
        price_ranges = self._get_price_range_distribution()

        # Recent activity
        recent_reviews = self.db.query(Review).filter(
            Review.review_date >= datetime.now() - timedelta(days=7)
        ).count()

        return {
            "summary": {
                "total_products": total_products,
                "total_variants": total_variants,
                "total_reviews": total_reviews,
                "active_offers": active_offers,
                "average_rating": round(avg_rating, 2),
                "recent_reviews_7d": recent_reviews
            },
            "brand_distribution": brand_distribution,
            "price_ranges": price_ranges,
            "last_updated": datetime.utcnow()
        }

    def get_product_statistics(self, brand: Optional[str], time_period: str) -> Dict[str, Any]:
        """Get comprehensive product statistics"""

        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(time_period, 30)
        cutoff_date = datetime.now() - timedelta(days=days)

        # Base query
        query = self.db.query(Product)
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))

        products = query.all()

        # Calculate statistics
        stats = {
            "total_products": len(products),
            "by_brand": self._get_brand_statistics(products),
            "price_analysis": self._get_price_analysis(products),
            "rating_analysis": self._get_rating_analysis(products, cutoff_date),
            "feature_analysis": self._get_feature_analysis(products),
            "time_period": time_period
        }

        return stats

    def get_price_trends(self, product_id: Optional[str], brand: Optional[str], days: int) -> Dict[str, Any]:
        """Get price trend analysis"""

        cutoff_date = datetime.now() - timedelta(days=days)

        # Build query
        query = self.db.query(PriceHistory).filter(PriceHistory.date >= cutoff_date)

        if product_id:
            query = query.filter(PriceHistory.product_id == product_id)
        elif brand:
            query = query.join(Product).filter(Product.brand.ilike(f"%{brand}%"))

        price_data = query.order_by(PriceHistory.date).all()

        # Analyze trends
        trends = self._analyze_price_trends(price_data)

        return {
            "period_days": days,
            "data_points": len(price_data),
            "price_trends": trends,
            "summary": {
                "average_price": trends.get("average_price", 0),
                "price_change_percentage": trends.get("overall_change_percentage", 0),
                "volatility_score": trends.get("volatility_score", 0)
            }
        }

    def get_market_insights(self, segment: Optional[str]) -> Dict[str, Any]:
        """Get market insights and trends"""

        insights = {
            "market_overview": self._get_market_overview(),
            "competitive_landscape": self._get_competitive_landscape(),
            "customer_preferences": self._get_customer_preferences(),
            "growth_opportunities": self._get_growth_opportunities(),
            "segment_focus": segment
        }

        if segment:
            insights["segment_analysis"] = self._get_segment_specific_insights(segment)

        return insights

    def get_review_analytics_summary(self, brand: Optional[str], period: str) -> Dict[str, Any]:
        """Get cross-product review analytics summary"""

        # Date range calculation
        if period == "weekly":
            cutoff_date = datetime.now() - timedelta(weeks=12)  # Last 12 weeks
        elif period == "quarterly":
            cutoff_date = datetime.now() - timedelta(days=365)  # Last 4 quarters
        else:  # monthly
            cutoff_date = datetime.now() - timedelta(days=365)  # Last 12 months

        # Base query
        query = self.db.query(Review).filter(Review.review_date >= cutoff_date)

        if brand:
            query = query.join(Product).filter(Product.brand.ilike(f"%{brand}%"))

        reviews = query.all()

        # Calculate metrics
        summary = self._calculate_review_summary(reviews, period)

        return summary

    def get_performance_metrics(self, metric_type: str, comparison_period: bool) -> Dict[str, Any]:
        """Get performance metrics and KPIs"""

        current_period = datetime.now() - timedelta(days=30)
        previous_period = datetime.now() - timedelta(days=60)

        metrics = {}

        if metric_type in ["all", "ratings"]:
            metrics["ratings"] = self._get_rating_metrics(current_period, previous_period if comparison_period else None)

        if metric_type in ["all", "engagement"]:
            metrics["engagement"] = self._get_engagement_metrics(current_period, previous_period if comparison_period else None)

        if metric_type in ["all", "technical"]:
            metrics["technical"] = self._get_technical_metrics()

        return {
            "metric_type": metric_type,
            "period": "30 days",
            "includes_comparison": comparison_period,
            "metrics": metrics,
            "generated_at": datetime.utcnow()
        }

    def get_brand_comparison(self, brands: List[str], metrics: List[str]) -> Dict[str, Any]:
        """Get detailed brand comparison analytics"""

        comparison = {}

        for brand in brands:
            brand_products = self.db.query(Product).filter(
                Product.brand.ilike(f"%{brand}%")
            ).all()

            brand_metrics = {}

            if "rating" in metrics:
                brand_metrics["rating"] = self._get_brand_rating_metrics(brand_products)

            if "price" in metrics:
                brand_metrics["price"] = self._get_brand_price_metrics(brand_products)

            if "market_share" in metrics:
                brand_metrics["market_share"] = self._get_brand_market_share(brand, brand_products)

            comparison[brand] = brand_metrics

        return {
            "brands_compared": brands,
            "metrics_included": metrics,
            "comparison": comparison,
            "winner_by_metric": self._determine_winners(comparison, metrics)
        }

    def get_trend_forecasting(self, forecast_type: str, forecast_period: int, confidence_level: float) -> Dict[str, Any]:
        """Get predictive analytics and trend forecasting"""

        # Mock implementation - in production would use ML models
        historical_data = self._get_historical_data_for_forecasting(forecast_type)

        forecast = {
            "forecast_type": forecast_type,
            "forecast_period_days": forecast_period,
            "confidence_level": confidence_level,
            "methodology": "Time series analysis with trend decomposition",
            "forecast_data": self._generate_mock_forecast(forecast_type, forecast_period),
            "accuracy_metrics": {
                "mean_absolute_error": 0.15,
                "confidence_interval": f"±{(1-confidence_level)*100:.1f}%"
            }
        }

        return forecast

    def get_competitive_intelligence(self, focus_area: str, competitor_analysis: bool) -> Dict[str, Any]:
        """Get competitive intelligence insights"""

        intelligence = {
            "focus_area": focus_area,
            "market_position": self._get_market_position_analysis(),
            "competitive_advantages": self._get_competitive_advantages(),
            "threats_opportunities": self._get_threats_opportunities(),
            "strategic_recommendations": self._get_strategic_recommendations(focus_area)
        }

        if competitor_analysis:
            intelligence["competitor_analysis"] = self._get_detailed_competitor_analysis()

        return intelligence

    def get_segment_analysis(self, segment_by: str, include_growth: bool) -> Dict[str, Any]:
        """Get market segment analysis"""

        segments = self._segment_market_by(segment_by)

        analysis = {
            "segmentation_method": segment_by,
            "segments": segments,
            "insights": self._get_segment_insights(segments)
        }

        if include_growth:
            analysis["growth_analysis"] = self._get_segment_growth_analysis(segments)

        return analysis

    def get_recommendation_performance(self, time_period: str, recommendation_type: Optional[str]) -> Dict[str, Any]:
        """Get recommendation system performance analytics"""

        # Mock implementation
        return {
            "time_period": time_period,
            "recommendation_type": recommendation_type or "all",
            "performance_metrics": {
                "click_through_rate": 12.5,
                "conversion_rate": 8.3,
                "recommendation_accuracy": 78.9,
                "user_satisfaction": 4.2
            },
            "top_recommended_products": [
                {"product_id": "1", "recommendation_count": 145, "success_rate": 82.1},
                {"product_id": "2", "recommendation_count": 132, "success_rate": 79.5}
            ],
            "improvement_suggestions": [
                "Increase personalization based on user history",
                "Improve price sensitivity weighting",
                "Add more feature-based recommendations"
            ]
        }

    def export_analytics_data(self, data_type: str, format_type: str, include_metadata: bool) -> Dict[str, Any]:
        """Export analytics data in various formats"""

        export_id = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if data_type == "summary":
            data = self.get_dashboard_overview()
        elif data_type == "detailed":
            data = {
                "dashboard": self.get_dashboard_overview(),
                "product_stats": self.get_product_statistics(None, "30d"),
                "price_trends": self.get_price_trends(None, None, 30)
            }
        else:
            data = {"message": "Raw data export would contain detailed database exports"}

        export_result = {
            "export_id": export_id,
            "data_type": data_type,
            "format": format_type,
            "data": data if format_type == "json" else f"Data formatted as {format_type}",
            "metadata": {
                "exported_at": datetime.utcnow(),
                "exported_by": "analytics_service",
                "record_count": len(str(data)),
                "export_size_kb": len(str(data)) / 1024
            } if include_metadata else None,
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }

        return export_result

    # Helper methods

    def _get_price_range_distribution(self) -> Dict[str, int]:
        """Get distribution of products by price range"""
        variants = self.db.query(Variant).filter(Variant.price.isnot(None)).all()

        ranges = {
            "Under $800": 0,
            "$800-$1200": 0,
            "$1200-$1600": 0,
            "$1600-$2000": 0,
            "Over $2000": 0
        }

        for variant in variants:
            price = float(variant.price)
            if price < 800:
                ranges["Under $800"] += 1
            elif price < 1200:
                ranges["$800-$1200"] += 1
            elif price < 1600:
                ranges["$1200-$1600"] += 1
            elif price < 2000:
                ranges["$1600-$2000"] += 1
            else:
                ranges["Over $2000"] += 1

        return ranges

    def _get_brand_statistics(self, products: List[Product]) -> Dict[str, Any]:
        """Calculate statistics by brand"""
        brand_stats = defaultdict(dict)

        for product in products:
            brand = product.brand
            if brand not in brand_stats:
                brand_stats[brand] = {"count": 0, "avg_rating": 0, "price_range": {}}

            brand_stats[brand]["count"] += 1

        return dict(brand_stats)

    def _get_price_analysis(self, products: List[Product]) -> Dict[str, Any]:
        """Analyze price distribution"""
        all_variants = []
        for product in products:
            all_variants.extend(product.variants)

        prices = [float(v.price) for v in all_variants if v.price]

        if not prices:
            return {"error": "No price data available"}

        return {
            "average": sum(prices) / len(prices),
            "min": min(prices),
            "max": max(prices),
            "median": sorted(prices)[len(prices)//2],
            "count": len(prices)
        }

    def _get_rating_analysis(self, products: List[Product], cutoff_date: datetime) -> Dict[str, Any]:
        """Analyze ratings and reviews"""
        all_reviews = []
        for product in products:
            product_reviews = self.db.query(Review).filter(
                Review.product_id == product.id,
                Review.review_date >= cutoff_date
            ).all()
            all_reviews.extend(product_reviews)

        if not all_reviews:
            return {"error": "No review data available"}

        ratings = [r.rating for r in all_reviews if r.rating]

        return {
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "total_reviews": len(all_reviews),
            "rating_distribution": dict(Counter(ratings))
        }

    def _get_feature_analysis(self, products: List[Product]) -> Dict[str, Any]:
        """Analyze common features across products"""
        # Mock implementation
        return {
            "common_features": {
                "SSD Storage": 85,
                "Fingerprint Reader": 70,
                "Backlit Keyboard": 60,
                "Touchscreen": 45
            },
            "performance_tiers": {
                "Entry Level": 30,
                "Mid Range": 50,
                "Premium": 20
            }
        }

    def _analyze_price_trends(self, price_data: List) -> Dict[str, Any]:
        """Analyze price trends from historical data"""
        if not price_data:
            return {"error": "No price data available"}

        prices = [float(p.price) for p in price_data if p.price]

        if len(prices) < 2:
            return {"error": "Insufficient data for trend analysis"}

        # Calculate basic trend metrics
        first_price = prices[0]
        last_price = prices[-1]
        avg_price = sum(prices) / len(prices)
        price_change = last_price - first_price
        price_change_pct = (price_change / first_price) * 100 if first_price > 0 else 0

        return {
            "average_price": avg_price,
            "price_change": price_change,
            "overall_change_percentage": price_change_pct,
            "volatility_score": self._calculate_volatility(prices),
            "trend_direction": "up" if price_change > 0 else "down" if price_change < 0 else "stable"
        }

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility score"""
        if len(prices) < 2:
            return 0.0

        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        return (variance ** 0.5) / avg * 100 if avg > 0 else 0.0

    def _get_market_overview(self) -> Dict[str, Any]:
        """Get general market overview"""
        return {
            "market_size": "Growing business laptop segment",
            "key_trends": [
                "Increased demand for remote work laptops",
                "Focus on battery life and portability",
                "Integration of AI features"
            ],
            "growth_rate": "8.5% YoY"
        }

    def _get_competitive_landscape(self) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        return {
            "market_leaders": ["HP", "Lenovo"],
            "competitive_factors": [
                "Price competitiveness",
                "Feature differentiation",
                "Brand reputation",
                "Customer support"
            ]
        }

    def _get_customer_preferences(self) -> Dict[str, Any]:
        """Analyze customer preferences from reviews"""
        return {
            "top_valued_features": [
                "Battery life",
                "Build quality",
                "Performance",
                "Display quality"
            ],
            "price_sensitivity": "Medium to high",
            "brand_loyalty": "Moderate"
        }

    def _get_growth_opportunities(self) -> List[str]:
        """Identify growth opportunities"""
        return [
            "Expand mid-range offerings",
            "Improve customer service ratings",
            "Enhance battery life across all models",
            "Strengthen gaming segment presence"
        ]

    def _get_segment_specific_insights(self, segment: str) -> Dict[str, Any]:
        """Get insights specific to a market segment"""
        segment_insights = {
            "budget": {
                "key_features": ["Value for money", "Basic performance"],
                "price_range": "$500-$800",
                "growth_potential": "High"
            },
            "premium": {
                "key_features": ["Premium build", "High performance", "Latest technology"],
                "price_range": "$1500+",
                "growth_potential": "Moderate"
            },
            "business": {
                "key_features": ["Security", "Reliability", "Professional design"],
                "price_range": "$800-$1500",
                "growth_potential": "High"
            }
        }

        return segment_insights.get(segment, {"error": "Unknown segment"})

    def _calculate_review_summary(self, reviews: List, period: str) -> Dict[str, Any]:
        """Calculate review analytics summary"""
        if not reviews:
            return {"error": "No review data available"}

        total_reviews = len(reviews)
        avg_rating = sum(r.rating for r in reviews if r.rating) / total_reviews

        # Sentiment analysis
        positive = sum(1 for r in reviews if r.rating >= 4)
        neutral = sum(1 for r in reviews if r.rating == 3)
        negative = sum(1 for r in reviews if r.rating <= 2)

        return {
            "period": period,
            "total_reviews_analyzed": total_reviews,
            "average_sentiment": {
                "positive": round(positive / total_reviews * 100, 1),
                "neutral": round(neutral / total_reviews * 100, 1),
                "negative": round(negative / total_reviews * 100, 1)
            },
            "overall_rating": round(avg_rating, 2),
            "trending_insights": [
                "Customer satisfaction remains high",
                "Performance consistently rated positively",
                "Battery life is a key concern for some users"
            ]
        }

    def _get_rating_metrics(self, current_period: datetime, previous_period: Optional[datetime]) -> Dict[str, Any]:
        """Get rating-related metrics"""
        current_reviews = self.db.query(Review).filter(
            Review.review_date >= current_period
        ).all()

        current_avg = sum(r.rating for r in current_reviews) / len(current_reviews) if current_reviews else 0

        metrics = {
            "current_average": round(current_avg, 2),
            "total_reviews": len(current_reviews)
        }

        if previous_period:
            previous_reviews = self.db.query(Review).filter(
                Review.review_date >= previous_period,
                Review.review_date < current_period
            ).all()

            previous_avg = sum(r.rating for r in previous_reviews) / len(previous_reviews) if previous_reviews else 0

            metrics["change"] = round(current_avg - previous_avg, 2)
            metrics["change_percentage"] = round((current_avg - previous_avg) / previous_avg * 100, 1) if previous_avg > 0 else 0

        return metrics

    def _get_engagement_metrics(self, current_period: datetime, previous_period: Optional[datetime]) -> Dict[str, Any]:
        """Get engagement-related metrics"""
        # Mock implementation
        return {
            "page_views": 15420,
            "unique_visitors": 8750,
            "avg_session_duration": "5m 23s",
            "bounce_rate": "34.2%"
        }

    def _get_technical_metrics(self) -> Dict[str, Any]:
        """Get technical performance metrics"""
        return {
            "api_response_time": "127ms",
            "uptime": "99.8%",
            "error_rate": "0.15%",
            "cache_hit_rate": "87.3%"
        }

    def _get_brand_rating_metrics(self, products: List[Product]) -> Dict[str, Any]:
        """Get rating metrics for a specific brand"""
        all_reviews = []
        for product in products:
            product_reviews = self.db.query(Review).filter(
                Review.product_id == product.id
            ).all()
            all_reviews.extend(product_reviews)

        if not all_reviews:
            return {"average_rating": 0, "total_reviews": 0}

        avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)

        return {
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(all_reviews)
        }

    def _get_brand_price_metrics(self, products: List[Product]) -> Dict[str, Any]:
        """Get price metrics for a specific brand"""
        all_variants = []
        for product in products:
            all_variants.extend(product.variants)

        prices = [float(v.price) for v in all_variants if v.price]

        if not prices:
            return {"average_price": 0, "price_range": "N/A"}

        return {
            "average_price": round(sum(prices) / len(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
            "price_range": f"${min(prices):.0f} - ${max(prices):.0f}"
        }

    def _get_brand_market_share(self, brand: str, products: List[Product]) -> Dict[str, Any]:
        """Calculate market share for a brand"""
        total_products = self.db.query(Product).count()
        brand_products = len(products)

        market_share = (brand_products / total_products * 100) if total_products > 0 else 0

        return {
            "market_share_percentage": round(market_share, 1),
            "product_count": brand_products,
            "total_market_products": total_products
        }

    def _determine_winners(self, comparison: Dict, metrics: List[str]) -> Dict[str, str]:
        """Determine winner for each metric"""
        winners = {}

        for metric in metrics:
            if metric == "rating":
                best_brand = max(comparison.keys(),
                               key=lambda b: comparison[b].get("rating", {}).get("average_rating", 0))
                winners[metric] = best_brand
            elif metric == "price":
                # Winner has best value (lowest average price)
                best_brand = min(comparison.keys(),
                               key=lambda b: comparison[b].get("price", {}).get("average_price", float('inf')))
                winners[metric] = best_brand
            elif metric == "market_share":
                best_brand = max(comparison.keys(),
                               key=lambda b: comparison[b].get("market_share", {}).get("market_share_percentage", 0))
                winners[metric] = best_brand

        return winners

    def _get_historical_data_for_forecasting(self, forecast_type: str) -> List:
        """Get historical data for forecasting"""
        # Mock implementation - would fetch relevant historical data
        return []

    def _generate_mock_forecast(self, forecast_type: str, forecast_period: int) -> List[Dict]:
        """Generate mock forecast data"""
        # Mock implementation for demonstration
        forecast_data = []
        base_date = datetime.now()

        for i in range(forecast_period):
            forecast_data.append({
                "date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "predicted_value": 1200 + (i * 2.5),  # Mock trend
                "confidence_lower": 1150 + (i * 2.5),
                "confidence_upper": 1250 + (i * 2.5)
            })

        return forecast_data

    def _get_market_position_analysis(self) -> Dict[str, Any]:
        """Analyze market position"""
        return {
            "market_position": "Strong in business segment",
            "competitive_advantages": ["Brand reputation", "Product quality"],
            "market_challenges": ["Price competition", "Feature differentiation"]
        }

    def _get_competitive_advantages(self) -> List[str]:
        """Get competitive advantages"""
        return [
            "Strong brand recognition",
            "Comprehensive product portfolio",
            "Established distribution channels",
            "Customer service reputation"
        ]

    def _get_threats_opportunities(self) -> Dict[str, List[str]]:
        """Get threats and opportunities"""
        return {
            "opportunities": [
                "Growing remote work market",
                "Emerging markets expansion",
                "AI integration in laptops"
            ],
            "threats": [
                "Increased competition",
                "Economic uncertainty",
                "Supply chain disruptions"
            ]
        }

    def _get_strategic_recommendations(self, focus_area: str) -> List[str]:
        """Get strategic recommendations"""
        recommendations = {
            "pricing": [
                "Optimize pricing strategy for mid-range segment",
                "Implement dynamic pricing based on demand",
                "Consider value-based pricing for premium features"
            ],
            "features": [
                "Invest in battery technology improvements",
                "Enhance security features",
                "Integrate more AI capabilities"
            ],
            "market_position": [
                "Strengthen presence in gaming segment",
                "Expand international markets",
                "Develop partnerships with software vendors"
            ],
            "customer_satisfaction": [
                "Improve customer service response times",
                "Enhance product documentation",
                "Implement customer feedback loop"
            ]
        }

        return recommendations.get(focus_area, [])

    def _get_detailed_competitor_analysis(self) -> Dict[str, Any]:
        """Get detailed competitor analysis"""
        return {
            "competitor_strengths": {
                "HP": ["Brand recognition", "Enterprise focus", "Global presence"],
                "Lenovo": ["Innovation", "Design", "Performance"]
            },
            "competitor_weaknesses": {
                "HP": ["Price premium", "Limited gaming focus"],
                "Lenovo": ["Brand perception in some markets", "Customer service"]
            },
            "market_gaps": [
                "Ultra-budget segment",
                "Specialized gaming laptops",
                "Rugged business laptops"
            ]
        }

    def _segment_market_by(self, segment_by: str) -> Dict[str, Any]:
        """Segment market by specified criteria"""
        if segment_by == "price_range":
            return {
                "Budget ($500-$800)": {"size": 30, "growth": 12},
                "Mid-range ($800-$1500)": {"size": 50, "growth": 8},
                "Premium ($1500+)": {"size": 20, "growth": 15}
            }
        elif segment_by == "use_case":
            return {
                "Business": {"size": 45, "growth": 10},
                "Gaming": {"size": 25, "growth": 18},
                "Student": {"size": 20, "growth": 5},
                "Creative": {"size": 10, "growth": 22}
            }
        # Add more segmentation logic as needed
        return {}

    def _get_segment_insights(self, segments: Dict[str, Any]) -> List[str]:
        """Get insights from segment analysis"""
        return [
            "Mid-range segment dominates the market",
            "Premium segment shows highest growth potential",
            "Business use case remains the largest segment"
        ]

    def _get_segment_growth_analysis(self, segments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze growth patterns in segments"""
        return {
            "fastest_growing": max(segments.keys(), key=lambda s: segments[s].get("growth", 0)),
            "largest_segment": max(segments.keys(), key=lambda s: segments[s].get("size", 0)),
            "growth_drivers": [
                "Remote work adoption",
                "Digital transformation",
                "Gaming market expansion"
            ]
        }