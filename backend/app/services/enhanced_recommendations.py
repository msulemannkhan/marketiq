"""
Enhanced Recommendation Service with constraints and rationale
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, cast, String
from decimal import Decimal
import logging
import uuid

from app.models import (
    Product, Variant, ReviewSummary, ReviewTheme, ProductOffer,
    UserPreference, UserRecommendation, ReviewAnalytics
)
from app.schemas.recommendations import (
    RecommendationConstraints, RecommendationRequest,
    ProductRecommendation, RecommendationResponse,
    ComparisonRecommendation, SmartRecommendation
)

logger = logging.getLogger(__name__)


class EnhancedRecommendationService:
    """Enhanced recommendation service with constraints and detailed rationale"""

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(
        self,
        request: RecommendationRequest,
        user_id: Optional[str] = None
    ) -> RecommendationResponse:
        """Get recommendations based on detailed constraints"""

        request_id = str(uuid.uuid4())
        constraints = request.constraints

        # Build base query
        query = self.db.query(Variant).join(Product).join(ReviewSummary, isouter=True)

        # Apply constraints
        query = self._apply_budget_constraints(query, constraints)
        query = self._apply_feature_constraints(query, constraints)
        query = self._apply_brand_constraints(query, constraints)
        query = self._apply_spec_constraints(query, constraints)
        query = self._apply_rating_constraints(query, constraints)

        # Get candidates
        candidates = query.limit(50).all()

        if not candidates:
            return RecommendationResponse(
                request_id=request_id,
                timestamp=datetime.utcnow(),
                constraints_summary=self._summarize_constraints(constraints),
                recommendations=[],
                no_match_reason="No products match the specified criteria"
            )

        # Score and rank candidates
        scored_variants = self._score_variants(
            candidates, constraints, request.user_context
        )

        # Build recommendations
        recommendations = []
        for variant, score, rationale in scored_variants[:request.max_results]:
            recommendation = self._build_product_recommendation(
                variant, score, rationale, constraints
            )
            recommendations.append(recommendation)

        # Get alternatives if requested
        alternatives = None
        if request.include_alternatives and len(scored_variants) > request.max_results:
            alternatives = []
            for variant, score, rationale in scored_variants[request.max_results:request.max_results + 3]:
                alt_recommendation = self._build_product_recommendation(
                    variant, score, rationale, constraints
                )
                alternatives.append(alt_recommendation)

        # Analyze trade-offs
        trade_offs = self._analyze_trade_offs(constraints, candidates)

        # Generate insights
        insights = self._generate_market_insights(constraints, candidates)

        # Store user recommendation if user provided
        if user_id and recommendations:
            self._store_user_recommendations(user_id, recommendations)

        return RecommendationResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            constraints_summary=self._summarize_constraints(constraints),
            recommendations=recommendations,
            alternatives=alternatives,
            trade_offs=trade_offs,
            insights=insights
        )

    def compare_products(
        self,
        product_ids: List[str],
        comparison_aspects: List[str] = None
    ) -> ComparisonRecommendation:
        """Compare multiple products with recommendation"""

        if not comparison_aspects:
            comparison_aspects = [
                "price", "performance", "battery_life", "build_quality", "value"
            ]

        # Get products and their best variants
        products_data = {}
        for product_id in product_ids:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                continue

            # Get best variant (lowest price with good specs)
            best_variant = self.db.query(Variant).filter(
                Variant.product_id == product_id
            ).order_by(Variant.price).first()

            if best_variant:
                products_data[product_id] = {
                    "product": product,
                    "variant": best_variant,
                    "review_summary": product.review_summary
                }

        # Perform detailed comparison
        detailed_comparison = {}
        for aspect in comparison_aspects:
            detailed_comparison[aspect] = self._compare_aspect(
                products_data, aspect
            )

        # Determine overall winner
        winner, winner_rationale = self._determine_winner(
            products_data, detailed_comparison
        )

        # Determine use case winners
        use_case_winners = self._determine_use_case_winners(products_data)

        # Generate verdict
        verdict = self._generate_comparison_verdict(
            products_data, winner, detailed_comparison
        )

        return ComparisonRecommendation(
            product_ids=product_ids,
            comparison_aspects=comparison_aspects,
            winner=winner,
            winner_rationale=winner_rationale,
            detailed_comparison=detailed_comparison,
            use_case_winners=use_case_winners,
            verdict=verdict
        )

    def get_smart_recommendations(
        self,
        recommendation_type: str = "budget_best"
    ) -> List[SmartRecommendation]:
        """Get curated smart recommendations"""

        recommendations = []

        if recommendation_type == "budget_best":
            recommendations.append(self._get_budget_best_recommendation())
        elif recommendation_type == "performance_best":
            recommendations.append(self._get_performance_best_recommendation())
        elif recommendation_type == "value_best":
            recommendations.append(self._get_value_best_recommendation())
        else:
            # Return all types
            recommendations.extend([
                self._get_budget_best_recommendation(),
                self._get_performance_best_recommendation(),
                self._get_value_best_recommendation()
            ])

        return [rec for rec in recommendations if rec]

    # Private helper methods

    def _apply_budget_constraints(
        self,
        query,
        constraints: RecommendationConstraints
    ):
        """Apply budget constraints to query"""

        if constraints.budget_min:
            query = query.filter(Variant.price >= constraints.budget_min)

        if constraints.budget_max:
            query = query.filter(Variant.price <= constraints.budget_max)

        return query

    def _apply_feature_constraints(
        self,
        query,
        constraints: RecommendationConstraints
    ):
        """Apply feature constraints to query"""

        for feature in constraints.must_have_features:
            feature_lower = feature.lower()

            if "touchscreen" in feature_lower:
                query = query.filter(
                    cast(Variant.additional_features['has_touchscreen'], String) == 'true'
                )
            elif "fingerprint" in feature_lower:
                query = query.filter(
                    cast(Variant.additional_features['has_fingerprint'], String) == 'true'
                )
            elif "backlit keyboard" in feature_lower:
                query = query.filter(
                    cast(Variant.additional_features['has_backlit_keyboard'], String) == 'true'
                )

        return query

    def _apply_brand_constraints(
        self,
        query,
        constraints: RecommendationConstraints
    ):
        """Apply brand constraints to query"""

        if constraints.brands:
            query = query.filter(Product.brand.in_(constraints.brands))

        return query

    def _apply_spec_constraints(
        self,
        query,
        constraints: RecommendationConstraints
    ):
        """Apply specification constraints to query"""

        if constraints.min_memory_gb:
            query = query.filter(Variant.memory_size >= constraints.min_memory_gb)

        if constraints.min_storage_gb:
            query = query.filter(Variant.storage_size >= constraints.min_storage_gb)

        if constraints.processor_preference:
            proc_pref = constraints.processor_preference.lower()
            if "intel" in proc_pref:
                query = query.filter(Variant.processor.ilike('%Intel%'))
            elif "amd" in proc_pref:
                query = query.filter(Variant.processor.ilike('%AMD%'))

        if constraints.display_size_preference:
            size_pref = constraints.display_size_preference
            if "14" in size_pref:
                query = query.filter(
                    Variant.display_size >= 13.9,
                    Variant.display_size <= 14.1
                )
            elif "15" in size_pref:
                query = query.filter(
                    Variant.display_size >= 15.0,
                    Variant.display_size <= 15.9
                )

        return query

    def _apply_rating_constraints(
        self,
        query,
        constraints: RecommendationConstraints
    ):
        """Apply rating constraints to query"""

        if constraints.min_rating:
            query = query.filter(
                ReviewSummary.average_rating >= constraints.min_rating
            )

        return query

    def _score_variants(
        self,
        variants: List[Variant],
        constraints: RecommendationConstraints,
        user_context: Optional[str] = None
    ) -> List[tuple]:
        """Score and rank variants based on constraints"""

        scored_variants = []

        for variant in variants:
            score, rationale = self._calculate_variant_score(
                variant, constraints, user_context
            )
            scored_variants.append((variant, score, rationale))

        # Sort by score descending
        scored_variants.sort(key=lambda x: x[1], reverse=True)

        return scored_variants

    def _calculate_variant_score(
        self,
        variant: Variant,
        constraints: RecommendationConstraints,
        user_context: Optional[str] = None
    ) -> tuple:
        """Calculate score and rationale for a variant"""

        score = 0
        rationale = {
            "score_breakdown": {},
            "strengths": [],
            "considerations": [],
            "match_reasons": []
        }

        # Budget score (30% weight)
        budget_score = self._score_budget_fit(variant, constraints)
        score += budget_score * 0.3
        rationale["score_breakdown"]["budget"] = budget_score

        # Specs score (25% weight)
        specs_score = self._score_specs_match(variant, constraints)
        score += specs_score * 0.25
        rationale["score_breakdown"]["specs"] = specs_score

        # Reviews score (20% weight)
        reviews_score = self._score_reviews(variant)
        score += reviews_score * 0.2
        rationale["score_breakdown"]["reviews"] = reviews_score

        # Features score (15% weight)
        features_score = self._score_features_match(variant, constraints)
        score += features_score * 0.15
        rationale["score_breakdown"]["features"] = features_score

        # Use case score (10% weight)
        use_case_score = self._score_use_case_fit(variant, constraints)
        score += use_case_score * 0.1
        rationale["score_breakdown"]["use_case"] = use_case_score

        # Generate rationale text
        self._populate_rationale_text(variant, constraints, rationale)

        return int(score), rationale

    def _score_budget_fit(
        self,
        variant: Variant,
        constraints: RecommendationConstraints
    ) -> int:
        """Score how well variant fits budget (0-100)"""

        if not variant.price:
            return 50

        price = float(variant.price)

        # If no budget constraints, score based on value
        if not constraints.budget_min and not constraints.budget_max:
            if price < 1000:
                return 90  # Great value
            elif price < 1500:
                return 75  # Good value
            else:
                return 60  # Premium pricing

        # Score based on budget range
        if constraints.budget_max:
            budget_max = float(constraints.budget_max)

            if price <= budget_max * 0.8:
                return 100  # Well under budget
            elif price <= budget_max * 0.9:
                return 85   # Good value within budget
            elif price <= budget_max:
                return 70   # At budget limit
            else:
                return 0    # Over budget

        return 75  # Default score

    def _score_specs_match(
        self,
        variant: Variant,
        constraints: RecommendationConstraints
    ) -> int:
        """Score specs match (0-100)"""

        score = 0
        max_score = 0

        # Memory scoring
        if constraints.min_memory_gb:
            max_score += 25
            if variant.memory_size and variant.memory_size >= constraints.min_memory_gb:
                if variant.memory_size >= constraints.min_memory_gb * 2:
                    score += 25  # Exceeds requirements
                else:
                    score += 20  # Meets requirements

        # Storage scoring
        if constraints.min_storage_gb:
            max_score += 25
            if variant.storage_size and variant.storage_size >= constraints.min_storage_gb:
                if variant.storage_size >= constraints.min_storage_gb * 2:
                    score += 25  # Exceeds requirements
                else:
                    score += 20  # Meets requirements

        # Processor scoring
        if constraints.processor_preference:
            max_score += 25
            proc_pref = constraints.processor_preference.lower()
            if variant.processor:
                variant_proc = variant.processor.lower()
                if proc_pref in variant_proc:
                    score += 25

        # Default good specs bonus
        if max_score == 0:
            max_score = 100
            score = 75  # Default good score

        return int((score / max_score) * 100) if max_score > 0 else 75

    def _score_reviews(self, variant: Variant) -> int:
        """Score based on reviews (0-100)"""

        if not variant.product.review_summary:
            return 60  # Neutral score for no reviews

        review_summary = variant.product.review_summary

        if not review_summary.average_rating:
            return 60

        rating = float(review_summary.average_rating)

        # Convert 1-5 rating to 0-100 score
        base_score = ((rating - 1) / 4) * 100

        # Bonus for number of reviews (more reviews = more confidence)
        review_count = review_summary.total_reviews or 0
        if review_count > 100:
            base_score += 10
        elif review_count > 50:
            base_score += 5

        return min(100, int(base_score))

    def _score_features_match(
        self,
        variant: Variant,
        constraints: RecommendationConstraints
    ) -> int:
        """Score feature matching (0-100)"""

        if not constraints.must_have_features and not constraints.nice_to_have_features:
            return 80  # No specific requirements

        score = 0
        total_features = len(constraints.must_have_features) + len(constraints.nice_to_have_features)

        if total_features == 0:
            return 80

        # Check must-have features (higher weight)
        for feature in constraints.must_have_features:
            if self._variant_has_feature(variant, feature):
                score += 60 / len(constraints.must_have_features) if constraints.must_have_features else 0

        # Check nice-to-have features
        for feature in constraints.nice_to_have_features:
            if self._variant_has_feature(variant, feature):
                score += 40 / len(constraints.nice_to_have_features) if constraints.nice_to_have_features else 0

        return min(100, int(score))

    def _score_use_case_fit(
        self,
        variant: Variant,
        constraints: RecommendationConstraints
    ) -> int:
        """Score use case fit (0-100)"""

        if not constraints.use_cases:
            return 75  # Neutral score

        # Use case scoring logic
        use_case_scores = {
            "business": self._score_business_use(variant),
            "programming": self._score_programming_use(variant),
            "gaming": self._score_gaming_use(variant),
            "travel": self._score_travel_use(variant),
            "student": self._score_student_use(variant)
        }

        total_score = 0
        for use_case in constraints.use_cases:
            use_case_lower = use_case.lower()
            for key, score in use_case_scores.items():
                if key in use_case_lower:
                    total_score += score
                    break

        return min(100, total_score // len(constraints.use_cases)) if constraints.use_cases else 75

    def _variant_has_feature(self, variant: Variant, feature: str) -> bool:
        """Check if variant has specific feature"""

        feature_lower = feature.lower()

        if not variant.additional_features:
            return False

        if "touchscreen" in feature_lower:
            return variant.additional_features.get("has_touchscreen", False)
        elif "fingerprint" in feature_lower:
            return variant.additional_features.get("has_fingerprint", False)
        elif "backlit" in feature_lower:
            return variant.additional_features.get("has_backlit_keyboard", False)

        return False

    def _score_business_use(self, variant: Variant) -> int:
        """Score variant for business use"""
        score = 70  # Base score

        # Prefer certain specs for business
        if variant.memory_size and variant.memory_size >= 16:
            score += 15

        if variant.storage_type and "SSD" in variant.storage_type:
            score += 10

        # Business laptops are often HP ProBook or ThinkPad
        if variant.product.model_family:
            model = variant.product.model_family.lower()
            if "probook" in model or "thinkpad" in model:
                score += 10

        return min(100, score)

    def _score_programming_use(self, variant: Variant) -> int:
        """Score variant for programming use"""
        score = 60  # Base score

        # Programming needs good RAM and fast storage
        if variant.memory_size and variant.memory_size >= 16:
            score += 20

        if variant.storage_type and "NVMe" in variant.storage_type:
            score += 15

        # Good processor
        if variant.processor and ("i7" in variant.processor or "Ultra" in variant.processor):
            score += 10

        return min(100, score)

    def _score_gaming_use(self, variant: Variant) -> int:
        """Score variant for gaming use"""
        score = 40  # Lower base since these are business laptops

        # Check for dedicated graphics
        if variant.graphics and ("MX" in variant.graphics or "RTX" in variant.graphics):
            score += 30

        if variant.memory_size and variant.memory_size >= 16:
            score += 15

        return min(100, score)

    def _score_travel_use(self, variant: Variant) -> int:
        """Score variant for travel use"""
        score = 70  # Base score

        # Prefer smaller, lighter laptops
        if variant.display_size and variant.display_size <= 14:
            score += 20

        # Battery life is important (would need real data)
        score += 10  # Assume decent battery life

        return min(100, score)

    def _score_student_use(self, variant: Variant) -> int:
        """Score variant for student use"""
        score = 80  # Base score

        # Students often need good value
        if variant.price and float(variant.price) < 1200:
            score += 15

        if variant.memory_size and variant.memory_size >= 8:
            score += 5

        return min(100, score)

    def _build_product_recommendation(
        self,
        variant: Variant,
        score: int,
        rationale: Dict,
        constraints: RecommendationConstraints
    ) -> ProductRecommendation:
        """Build a product recommendation from variant and score"""

        # Get offers for this product
        offers = self.db.query(ProductOffer).filter(
            ProductOffer.product_id == variant.product_id,
            ProductOffer.active == True
        ).all()

        # Get review themes for pros/cons
        themes = self.db.query(ReviewTheme).filter(
            ReviewTheme.product_id == variant.product_id
        ).order_by(desc(ReviewTheme.mention_count)).limit(5).all()

        pros = [theme.theme for theme in themes if theme.sentiment == "positive"][:3]
        cons = [theme.theme for theme in themes if theme.sentiment == "negative"][:2]

        # Generate best_for based on use cases and features
        best_for = self._generate_best_for(variant, constraints)

        # Generate citations
        citations = [
            {
                "source": "Product Specifications",
                "url": variant.product.pdf_spec_url or "",
                "type": "specs"
            }
        ]

        if variant.product.review_summary:
            citations.append({
                "source": f"{variant.product.review_summary.total_reviews} customer reviews",
                "url": variant.product.product_url or "",
                "type": "reviews"
            })

        return ProductRecommendation(
            product_id=variant.product_id,
            variant_id=variant.id,
            product_name=variant.product.product_name,
            brand=variant.product.brand,
            price=variant.price,
            match_score=score,
            rationale=rationale,
            pros=pros,
            cons=cons,
            best_for=best_for,
            citations=citations
        )

    def _generate_best_for(
        self,
        variant: Variant,
        constraints: RecommendationConstraints
    ) -> List[str]:
        """Generate best_for list based on variant and constraints"""

        best_for = []

        # Based on use cases
        for use_case in constraints.use_cases:
            best_for.append(f"{use_case} professionals")

        # Based on specs
        if variant.memory_size and variant.memory_size >= 16:
            best_for.append("Power users")

        if variant.display_size and variant.display_size <= 14:
            best_for.append("Mobile professionals")

        return best_for[:3]

    def _summarize_constraints(self, constraints: RecommendationConstraints) -> str:
        """Create human-readable summary of constraints"""

        parts = []

        if constraints.budget_max:
            parts.append(f"Budget: ${constraints.budget_max}")

        if constraints.must_have_features:
            parts.append(f"Required: {', '.join(constraints.must_have_features)}")

        if constraints.use_cases:
            parts.append(f"Use: {', '.join(constraints.use_cases)}")

        if constraints.brands:
            parts.append(f"Brands: {', '.join(constraints.brands)}")

        return "; ".join(parts) if parts else "No specific constraints"

    def _analyze_trade_offs(
        self,
        constraints: RecommendationConstraints,
        candidates: List[Variant]
    ) -> List[str]:
        """Analyze trade-offs in recommendations"""

        trade_offs = []

        if constraints.budget_max:
            budget_max = float(constraints.budget_max)
            over_budget = [c for c in candidates if c.price and float(c.price) > budget_max]

            if over_budget:
                trade_offs.append(
                    f"Consider increasing budget by ${min(over_budget, key=lambda x: x.price).price - budget_max:.0f} "
                    "for significantly better options"
                )

        # Check for missing must-have features
        if constraints.must_have_features:
            missing_features = []
            for feature in constraints.must_have_features:
                has_feature = any(
                    self._variant_has_feature(c, feature) for c in candidates[:5]
                )
                if not has_feature:
                    missing_features.append(feature)

            if missing_features:
                trade_offs.append(
                    f"Limited options with: {', '.join(missing_features)}"
                )

        return trade_offs

    def _generate_market_insights(
        self,
        constraints: RecommendationConstraints,
        candidates: List[Variant]
    ) -> List[str]:
        """Generate market insights from available options"""

        insights = []

        if candidates:
            # Price insights
            prices = [float(c.price) for c in candidates if c.price]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)

                insights.append(
                    f"Price range: ${min_price:.0f} - ${max_price:.0f} "
                    f"(avg: ${avg_price:.0f})"
                )

            # Brand insights
            brands = {}
            for candidate in candidates[:10]:
                brand = candidate.product.brand
                brands[brand] = brands.get(brand, 0) + 1

            if brands:
                top_brand = max(brands.items(), key=lambda x: x[1])
                insights.append(f"{top_brand[0]} has most options ({top_brand[1]} models)")

        return insights

    def _store_user_recommendations(
        self,
        user_id: str,
        recommendations: List[ProductRecommendation]
    ):
        """Store recommendations for user tracking"""

        for rec in recommendations:
            user_rec = UserRecommendation(
                user_id=user_id,
                product_id=rec.product_id,
                variant_id=rec.variant_id,
                recommendation_type="constraint_based",
                score=rec.match_score,
                rationale=rec.rationale,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            self.db.add(user_rec)

        self.db.commit()

    def _compare_aspect(self, products_data: Dict, aspect: str) -> Dict:
        """Compare specific aspect across products"""

        comparison = {}

        for product_id, data in products_data.items():
            variant = data["variant"]
            review_summary = data["review_summary"]

            if aspect == "price":
                comparison[product_id] = {
                    "value": float(variant.price) if variant.price else 0,
                    "display": f"${variant.price}" if variant.price else "N/A"
                }
            elif aspect == "performance":
                # Simple performance score based on processor and memory
                score = 50
                if variant.processor and ("i7" in variant.processor or "Ultra" in variant.processor):
                    score += 25
                if variant.memory_size and variant.memory_size >= 16:
                    score += 25

                comparison[product_id] = {
                    "value": score,
                    "display": f"{score}/100"
                }
            elif aspect == "battery_life":
                # Would need real battery data, using placeholder
                comparison[product_id] = {
                    "value": 75,
                    "display": "8-10 hours (est.)"
                }
            elif aspect == "build_quality":
                # Use review rating as proxy
                rating = float(review_summary.average_rating) if review_summary and review_summary.average_rating else 3.5
                score = int((rating / 5) * 100)
                comparison[product_id] = {
                    "value": score,
                    "display": f"{rating}/5 stars"
                }
            elif aspect == "value":
                # Price to performance ratio
                price = float(variant.price) if variant.price else 1500
                performance_score = 50
                if variant.memory_size and variant.memory_size >= 16:
                    performance_score += 25
                if variant.storage_type and "SSD" in variant.storage_type:
                    performance_score += 15

                value_score = int((performance_score / price) * 10000)
                comparison[product_id] = {
                    "value": value_score,
                    "display": f"{value_score} pts"
                }

        return comparison

    def _determine_winner(self, products_data: Dict, detailed_comparison: Dict) -> tuple:
        """Determine overall winner from comparison"""

        if not products_data:
            return None, "No products to compare"

        # Simple scoring: best average rank across aspects
        product_scores = {}

        for aspect, comparison in detailed_comparison.items():
            if not comparison:
                continue

            # Rank products for this aspect
            sorted_products = sorted(
                comparison.items(),
                key=lambda x: x[1]["value"],
                reverse=True
            )

            for rank, (product_id, _) in enumerate(sorted_products):
                product_scores[product_id] = product_scores.get(product_id, 0) + (len(sorted_products) - rank)

        if not product_scores:
            return None, "Unable to determine winner"

        winner = max(product_scores.items(), key=lambda x: x[1])[0]
        winner_product = products_data[winner]["product"]

        rationale = f"{winner_product.product_name} wins with best overall balance across price, performance, and features"

        return winner, rationale

    def _determine_use_case_winners(self, products_data: Dict) -> Dict[str, str]:
        """Determine best product for different use cases"""

        use_case_winners = {}

        if not products_data:
            return use_case_winners

        # Business use - favor reliability and features
        business_scores = {}
        for product_id, data in products_data.items():
            score = 0
            variant = data["variant"]

            if variant.memory_size and variant.memory_size >= 16:
                score += 20
            if variant.storage_type and "SSD" in variant.storage_type:
                score += 15
            if data["product"].brand in ["HP", "Lenovo"]:
                score += 10

            business_scores[product_id] = score

        if business_scores:
            use_case_winners["business"] = max(business_scores.items(), key=lambda x: x[1])[0]

        # Budget use - favor price
        budget_winner = min(
            products_data.items(),
            key=lambda x: float(x[1]["variant"].price) if x[1]["variant"].price else 9999
        )[0]
        use_case_winners["budget"] = budget_winner

        return use_case_winners

    def _generate_comparison_verdict(
        self,
        products_data: Dict,
        winner: Optional[str],
        detailed_comparison: Dict
    ) -> str:
        """Generate comparison verdict summary"""

        if not winner or winner not in products_data:
            return "All products have similar value propositions with different strengths"

        winner_product = products_data[winner]["product"]
        return f"{winner_product.product_name} offers the best overall value with strong performance and competitive pricing"

    def _get_budget_best_recommendation(self) -> Optional[SmartRecommendation]:
        """Get best budget recommendation"""

        # Find best value under $1200
        variants = self.db.query(Variant).join(Product).filter(
            Variant.price <= 1200
        ).order_by(Variant.price).limit(3).all()

        if not variants:
            return None

        products = []
        for variant in variants:
            rec = self._build_product_recommendation(
                variant, 85, {"match_reasons": ["Best value for budget"]},
                RecommendationConstraints(budget_max=1200)
            )
            products.append(rec)

        return SmartRecommendation(
            recommendation_type="budget_best",
            title="Best Budget Business Laptops",
            description="Top value laptops under $1,200 that don't compromise on essential features",
            products=products,
            target_audience=["students", "small businesses", "budget-conscious buyers"],
            key_benefits=["Affordable pricing", "Essential business features", "Reliable performance"],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )

    def _get_performance_best_recommendation(self) -> Optional[SmartRecommendation]:
        """Get best performance recommendation"""

        # Find best performance variants
        variants = self.db.query(Variant).join(Product).filter(
            Variant.memory_size >= 16
        ).order_by(desc(Variant.memory_size)).limit(3).all()

        if not variants:
            return None

        products = []
        for variant in variants:
            rec = self._build_product_recommendation(
                variant, 90, {"match_reasons": ["High performance specs"]},
                RecommendationConstraints(min_memory_gb=16)
            )
            products.append(rec)

        return SmartRecommendation(
            recommendation_type="performance_best",
            title="High Performance Business Laptops",
            description="Top-tier laptops for demanding workloads and professional applications",
            products=products,
            target_audience=["power users", "developers", "creative professionals"],
            key_benefits=["High-end processors", "Ample RAM", "Fast storage"],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )

    def _get_value_best_recommendation(self) -> Optional[SmartRecommendation]:
        """Get best value recommendation"""

        # Find best price-to-performance ratio
        variants = self.db.query(Variant).join(Product).join(ReviewSummary).filter(
            ReviewSummary.average_rating >= 4.0,
            Variant.price <= 1500
        ).order_by(desc(ReviewSummary.average_rating)).limit(3).all()

        if not variants:
            return None

        products = []
        for variant in variants:
            rec = self._build_product_recommendation(
                variant, 88, {"match_reasons": ["Best price-performance ratio"]},
                RecommendationConstraints(min_rating=4.0, budget_max=1500)
            )
            products.append(rec)

        return SmartRecommendation(
            recommendation_type="value_best",
            title="Best Value Business Laptops",
            description="Perfect balance of price, performance, and features for most users",
            products=products,
            target_audience=["professionals", "general users", "value seekers"],
            key_benefits=["Balanced performance", "Good pricing", "Strong reviews"],
            valid_until=datetime.utcnow() + timedelta(days=30)
        )

    def _populate_rationale_text(
        self,
        variant: Variant,
        constraints: RecommendationConstraints,
        rationale: Dict
    ):
        """Populate human-readable rationale text"""

        strengths = []
        considerations = []
        match_reasons = []

        # Analyze budget fit
        if variant.price and constraints.budget_max:
            price = float(variant.price)
            budget_max = float(constraints.budget_max)

            if price <= budget_max * 0.8:
                strengths.append("Excellent value - well under budget")
                match_reasons.append("Great price point")
            elif price <= budget_max:
                match_reasons.append("Fits within budget")

        # Analyze specs
        if variant.memory_size and variant.memory_size >= 16:
            strengths.append("Generous 16GB+ RAM for multitasking")

        if variant.storage_type and "NVMe" in variant.storage_type:
            strengths.append("Fast NVMe SSD storage")

        # Analyze reviews
        if variant.product.review_summary and variant.product.review_summary.average_rating:
            rating = float(variant.product.review_summary.average_rating)
            if rating >= 4.5:
                strengths.append("Exceptionally well-reviewed")
            elif rating >= 4.0:
                strengths.append("Highly rated by customers")
            else:
                considerations.append("Mixed customer reviews")

        # Populate rationale
        rationale["strengths"] = strengths
        rationale["considerations"] = considerations
        rationale["match_reasons"] = match_reasons