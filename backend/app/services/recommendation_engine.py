from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, cast, String
from app.models import Product, Variant, ReviewSummary
import re


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    async def get_recommendations(
        self,
        budget: Optional[float] = None,
        requirements: List[str] = None,
        preferences: List[str] = None,
        use_case: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Generate product recommendations based on criteria"""

        # Build base query
        query = self.db.query(Variant).join(Product)

        # Apply budget filter
        if budget:
            query = query.filter(Variant.price <= budget)

        # Apply requirement filters
        if requirements:
            for req in requirements:
                query = self._apply_requirement_filter(query, req)

        # Apply use case filters
        if use_case:
            query = self._apply_use_case_filter(query, use_case)

        # Get candidates
        variants = query.limit(20).all()  # Get more for scoring

        # Score and rank variants
        scored_variants = self._score_variants(variants, preferences, use_case, budget)

        # Format and return top recommendations
        return [self._format_recommendation(v) for v in scored_variants[:limit]]

    def _apply_requirement_filter(self, query, requirement: str):
        """Apply specific requirement filter to query"""
        req_lower = requirement.lower()

        # Memory requirements
        if "16gb" in req_lower and "ram" in req_lower:
            query = query.filter(Variant.memory_size >= 16)
        elif "32gb" in req_lower and "ram" in req_lower:
            query = query.filter(Variant.memory_size >= 32)
        elif "8gb" in req_lower and "ram" in req_lower:
            query = query.filter(Variant.memory_size >= 8)

        # Storage requirements
        elif "ssd" in req_lower:
            query = query.filter(Variant.storage_type.ilike('%SSD%'))
        elif "nvme" in req_lower:
            query = query.filter(Variant.storage_type.ilike('%NVMe%'))
        elif "512gb" in req_lower and "storage" in req_lower:
            query = query.filter(Variant.storage_size >= 512)
        elif "1tb" in req_lower:
            query = query.filter(Variant.storage_size >= 1000)

        # Display requirements
        elif "touchscreen" in req_lower:
            query = query.filter(
                cast(Variant.additional_features['has_touchscreen'], String) == 'true'
            )
        elif "14 inch" in req_lower or "14\"" in req_lower:
            query = query.filter(Variant.display_size >= 13.9, Variant.display_size <= 14.1)

        # Security features
        elif "fingerprint" in req_lower:
            query = query.filter(
                cast(Variant.additional_features['has_fingerprint'], String) == 'true'
            )

        # Processor requirements
        elif "intel" in req_lower:
            query = query.filter(Variant.processor.ilike('%Intel%'))
        elif "amd" in req_lower:
            query = query.filter(Variant.processor.ilike('%AMD%'))
        elif "core ultra" in req_lower:
            query = query.filter(Variant.processor.ilike('%Core Ultra%'))

        return query

    def _apply_use_case_filter(self, query, use_case: str):
        """Apply filters based on use case"""
        use_case_lower = use_case.lower()

        if "programming" in use_case_lower or "development" in use_case_lower:
            # Prefer higher memory and fast processors
            query = query.filter(Variant.memory_size >= 16)
            query = query.filter(Variant.storage_type.ilike('%SSD%'))

        elif "business" in use_case_lower or "office" in use_case_lower:
            # Standard business requirements
            query = query.filter(Variant.memory_size >= 8)
            query = query.filter(Variant.storage_type.ilike('%SSD%'))

        elif "gaming" in use_case_lower or "graphics" in use_case_lower:
            # Prefer dedicated graphics and higher specs
            query = query.filter(Variant.memory_size >= 16)
            query = query.filter(Variant.graphics.isnot(None))

        elif "travel" in use_case_lower or "portable" in use_case_lower:
            # Prefer smaller, lighter laptops
            query = query.filter(Variant.display_size <= 14)

        return query

    def _score_variants(
        self,
        variants: List[Variant],
        preferences: List[str] = None,
        use_case: Optional[str] = None,
        budget: Optional[float] = None
    ) -> List[Variant]:
        """Score variants based on preferences and use case"""

        scored_variants = []

        for variant in variants:
            score = 0.0

            # Base score from specifications
            score += self._calculate_spec_score(variant)

            # Preference-based scoring
            if preferences:
                score += self._calculate_preference_score(variant, preferences)

            # Use case scoring
            if use_case:
                score += self._calculate_use_case_score(variant, use_case)

            # Budget efficiency scoring
            if budget and variant.price:
                score += self._calculate_budget_score(variant, budget)

            # Brand reputation scoring
            score += self._calculate_brand_score(variant)

            variant.recommendation_score = score
            scored_variants.append(variant)

        # Sort by score
        return sorted(scored_variants, key=lambda x: x.recommendation_score, reverse=True)

    def _calculate_spec_score(self, variant: Variant) -> float:
        """Calculate score based on specifications quality"""
        score = 0.0

        # Memory scoring
        if variant.memory_size:
            if variant.memory_size >= 32:
                score += 15
            elif variant.memory_size >= 16:
                score += 10
            elif variant.memory_size >= 8:
                score += 5

        # Storage scoring
        if variant.storage_type:
            if "NVMe" in variant.storage_type:
                score += 10
            elif "SSD" in variant.storage_type:
                score += 7
            elif "HDD" in variant.storage_type:
                score += 2

        if variant.storage_size:
            if variant.storage_size >= 1000:  # 1TB+
                score += 8
            elif variant.storage_size >= 512:
                score += 5
            elif variant.storage_size >= 256:
                score += 3

        # Processor scoring
        if variant.processor:
            if "Core Ultra" in variant.processor:
                score += 12
            elif "Core i7" in variant.processor:
                score += 10
            elif "Core i5" in variant.processor:
                score += 8
            elif "Ryzen 7" in variant.processor:
                score += 10
            elif "Ryzen 5" in variant.processor:
                score += 8

        return score

    def _calculate_preference_score(self, variant: Variant, preferences: List[str]) -> float:
        """Calculate score based on user preferences"""
        score = 0.0

        for pref in preferences:
            pref_lower = pref.lower()

            if "lightweight" in pref_lower or "portable" in pref_lower:
                if variant.display_size and variant.display_size <= 14:
                    score += 8

            elif "battery life" in pref_lower or "battery" in pref_lower:
                # U-series processors are more efficient
                if variant.processor and "U" in variant.processor:
                    score += 8

            elif "performance" in pref_lower or "fast" in pref_lower:
                if variant.memory_size and variant.memory_size >= 16:
                    score += 6
                if variant.storage_type and "NVMe" in variant.storage_type:
                    score += 6

            elif "budget" in pref_lower or "affordable" in pref_lower:
                if variant.price and variant.price < 1200:
                    score += 8

            elif "touchscreen" in pref_lower:
                if variant.additional_features.get('has_touchscreen'):
                    score += 10

            elif "security" in pref_lower:
                if variant.additional_features.get('has_fingerprint'):
                    score += 6

        return score

    def _calculate_use_case_score(self, variant: Variant, use_case: str) -> float:
        """Calculate score based on use case suitability"""
        score = 0.0
        use_case_lower = use_case.lower()

        if "programming" in use_case_lower or "development" in use_case_lower:
            if variant.memory_size and variant.memory_size >= 16:
                score += 10
            if variant.storage_type and "SSD" in variant.storage_type:
                score += 8
            if variant.display_size and variant.display_size >= 14:
                score += 5

        elif "business" in use_case_lower or "office" in use_case_lower:
            if variant.memory_size and variant.memory_size >= 8:
                score += 6
            if variant.additional_features.get('has_fingerprint'):
                score += 8
            if variant.price and variant.price <= 1500:
                score += 5

        elif "travel" in use_case_lower:
            if variant.display_size and variant.display_size <= 14:
                score += 10
            if variant.processor and "U" in variant.processor:
                score += 8

        return score

    def _calculate_budget_score(self, variant: Variant, budget: float) -> float:
        """Calculate score based on budget efficiency"""
        if not variant.price:
            return 0

        # Reward variants that offer good value within budget
        if variant.price <= budget * 0.8:  # Under 80% of budget
            return 8
        elif variant.price <= budget * 0.9:  # Under 90% of budget
            return 6
        elif variant.price <= budget:  # Within budget
            return 4
        else:
            return 0

    def _calculate_brand_score(self, variant: Variant) -> float:
        """Calculate score based on brand reputation for business use"""
        brand = variant.product.brand.lower()

        # Both HP and Lenovo are excellent for business
        if brand == "hp":
            return 5
        elif brand == "lenovo":
            return 5
        else:
            return 0

    def _format_recommendation(self, variant: Variant) -> Dict:
        """Format variant as recommendation response"""
        return {
            "variant_id": str(variant.id),
            "product_name": variant.product.product_name,
            "brand": variant.product.brand,
            "model_family": variant.product.model_family,
            "sku": variant.variant_sku,
            "configuration": {
                "processor": variant.processor,
                "memory": variant.memory,
                "storage": variant.storage,
                "display": variant.display,
                "graphics": variant.graphics
            },
            "price": float(variant.price) if variant.price else None,
            "availability": variant.availability,
            "score": round(variant.recommendation_score, 2),
            "rationale": self._generate_rationale(variant),
            "key_features": self._extract_key_features(variant),
            "url": variant.product.product_url
        }

    def _generate_rationale(self, variant: Variant) -> str:
        """Generate explanation for recommendation"""
        reasons = []

        # Price-based reasons
        if variant.price:
            if variant.price < 1000:
                reasons.append("excellent value for money")
            elif variant.price < 1500:
                reasons.append("good balance of features and price")

        # Spec-based reasons
        if variant.memory_size:
            if variant.memory_size >= 16:
                reasons.append("ample memory for multitasking")
            elif variant.memory_size >= 8:
                reasons.append("sufficient memory for office tasks")

        if variant.storage_type:
            if "NVMe" in variant.storage_type:
                reasons.append("ultra-fast NVMe storage")
            elif "SSD" in variant.storage_type:
                reasons.append("fast SSD storage")

        if variant.processor:
            if "Core Ultra" in variant.processor:
                reasons.append("latest Intel Core Ultra processor")
            elif "Core i7" in variant.processor:
                reasons.append("high-performance Intel Core i7")
            elif "Ryzen" in variant.processor:
                reasons.append("efficient AMD Ryzen processor")

        # Feature-based reasons
        if variant.additional_features.get('has_fingerprint'):
            reasons.append("enhanced security with fingerprint reader")

        if variant.additional_features.get('has_touchscreen'):
            reasons.append("modern touchscreen display")

        if not reasons:
            reasons.append("meets your specified requirements")

        return f"Recommended because it offers {', '.join(reasons)}"

    def _extract_key_features(self, variant: Variant) -> List[str]:
        """Extract key selling points for the variant"""
        features = []

        if variant.processor:
            features.append(f"Processor: {variant.processor}")

        if variant.memory:
            features.append(f"Memory: {variant.memory}")

        if variant.storage:
            features.append(f"Storage: {variant.storage}")

        if variant.display:
            features.append(f"Display: {variant.display}")

        # Add special features
        if variant.additional_features.get('has_touchscreen'):
            features.append("Touchscreen")

        if variant.additional_features.get('has_fingerprint'):
            features.append("Fingerprint Reader")

        if variant.additional_features.get('has_backlit_keyboard'):
            features.append("Backlit Keyboard")

        return features

    async def get_similar_products(self, variant_id: str, limit: int = 3) -> List[Dict]:
        """Get products similar to the specified variant"""
        target_variant = self.db.query(Variant).filter(Variant.id == variant_id).first()

        if not target_variant:
            return []

        # Find similar variants based on specs
        query = self.db.query(Variant).join(Product).filter(
            Variant.id != variant_id
        )

        # Similar price range (±20%)
        if target_variant.price:
            price_min = target_variant.price * 0.8
            price_max = target_variant.price * 1.2
            query = query.filter(
                and_(Variant.price >= price_min, Variant.price <= price_max)
            )

        # Similar memory size
        if target_variant.memory_size:
            query = query.filter(Variant.memory_size == target_variant.memory_size)

        # Similar processor family
        if target_variant.processor_family:
            query = query.filter(Variant.processor_family == target_variant.processor_family)

        similar_variants = query.limit(limit).all()

        return [self._format_recommendation(v) for v in similar_variants]