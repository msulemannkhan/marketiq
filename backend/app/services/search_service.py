from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from app.models import Product, Variant
from app.schemas.search import SearchFilters, SearchResult, VariantWithProduct
import re


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    async def search(
        self,
        query: Optional[str] = None,
        filters: Optional[SearchFilters] = None,
        sort_by: str = "price",
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> List[SearchResult]:
        """Search variants with optional filters and sorting"""

        # Base query with joins
        base_query = self.db.query(Variant).join(Product)

        # Apply text search
        if query:
            search_conditions = self._build_text_search_conditions(query)
            base_query = base_query.filter(or_(*search_conditions))

        # Apply filters
        if filters:
            base_query = self._apply_filters(base_query, filters)

        # Apply sorting
        base_query = self._apply_sorting(base_query, sort_by, sort_order)

        # Apply pagination
        variants = base_query.offset(offset).limit(limit).all()

        # Convert to search results with relevance scoring
        results = []
        for variant in variants:
            relevance_score = self._calculate_relevance_score(variant, query, filters)
            match_reasons = self._get_match_reasons(variant, query, filters)

            # Create VariantWithProduct object
            variant_with_product = VariantWithProduct(
                id=variant.id,
                product_id=variant.product_id,
                variant_sku=variant.variant_sku,
                processor=variant.processor,
                processor_family=variant.processor_family,
                processor_speed=variant.processor_speed,
                memory=variant.memory,
                memory_size=variant.memory_size,
                memory_type=variant.memory_type,
                storage=variant.storage,
                storage_size=variant.storage_size,
                storage_type=variant.storage_type,
                display=variant.display,
                display_size=variant.display_size,
                display_resolution=variant.display_resolution,
                graphics=variant.graphics,
                additional_features=variant.additional_features or {},
                price=variant.price,
                availability=variant.availability,
                created_at=variant.created_at,
                product_name=variant.product.product_name,
                brand=variant.product.brand,
                model_family=variant.product.model_family
            )

            results.append(SearchResult(
                variant=variant_with_product,
                relevance_score=relevance_score,
                match_reasons=match_reasons
            ))

        return results

    def _build_text_search_conditions(self, query: str) -> List:
        """Build search conditions for text query"""
        search_terms = query.lower().split()
        conditions = []

        for term in search_terms:
            term_conditions = [
                Product.product_name.ilike(f"%{term}%"),
                Product.brand.ilike(f"%{term}%"),
                Product.model_family.ilike(f"%{term}%"),
                Variant.processor.ilike(f"%{term}%"),
                Variant.processor_family.ilike(f"%{term}%"),
                Variant.memory.ilike(f"%{term}%"),
                Variant.storage.ilike(f"%{term}%"),
                Variant.graphics.ilike(f"%{term}%")
            ]
            conditions.append(or_(*term_conditions))

        return conditions

    def _apply_filters(self, query, filters: SearchFilters):
        """Apply search filters to query"""
        if filters.brand:
            query = query.filter(Product.brand.ilike(f"%{filters.brand}%"))

        if filters.min_price is not None and filters.min_price > 0:
            query = query.filter(Variant.price >= filters.min_price)

        if filters.max_price is not None and filters.max_price > 0:
            query = query.filter(Variant.price <= filters.max_price)

        if filters.processor_family:
            query = query.filter(Variant.processor_family.ilike(f"%{filters.processor_family}%"))

        if filters.min_memory is not None and filters.min_memory > 0:
            query = query.filter(Variant.memory_size >= filters.min_memory)

        if filters.storage_type:
            query = query.filter(Variant.storage_type.ilike(f"%{filters.storage_type}%"))

        if filters.min_storage_size is not None and filters.min_storage_size > 0:
            query = query.filter(Variant.storage_size >= filters.min_storage_size)


        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """Apply sorting to query"""
        sort_column = None

        if sort_by == "price":
            sort_column = Variant.price
        elif sort_by == "name":
            sort_column = Product.product_name
        elif sort_by == "performance":
            # Sort by processor family and memory size as a proxy for performance
            if sort_order == "desc":
                return query.order_by(desc(Variant.memory_size), desc(Variant.processor_family))
            else:
                return query.order_by(asc(Variant.memory_size), asc(Variant.processor_family))

        if sort_column is not None:
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

        return query

    def _calculate_relevance_score(
        self,
        variant: Variant,
        query: Optional[str],
        filters: Optional[SearchFilters]
    ) -> float:
        """Calculate relevance score for a variant"""
        score = 0.0

        if query:
            # Score based on text matches
            query_lower = query.lower()
            text_fields = [
                variant.product.product_name,
                variant.product.brand,
                variant.product.model_family,
                variant.processor,
                variant.memory,
                variant.storage
            ]

            for field in text_fields:
                if field and query_lower in field.lower():
                    score += 0.2

        # Score based on filter matches
        if filters:
            if filters.brand and variant.product.brand.lower() == filters.brand.lower():
                score += 0.3

            if filters.processor_family and variant.processor_family:
                if filters.processor_family.lower() in variant.processor_family.lower():
                    score += 0.25

        # Normalize score to 0-1 range
        return min(score, 1.0)

    def _get_match_reasons(
        self,
        variant: Variant,
        query: Optional[str],
        filters: Optional[SearchFilters]
    ) -> List[str]:
        """Get reasons why this variant matched the search"""
        reasons = []

        if query:
            query_lower = query.lower()
            if query_lower in variant.product.product_name.lower():
                reasons.append(f"Product name contains '{query}'")
            if variant.processor and query_lower in variant.processor.lower():
                reasons.append(f"Processor matches '{query}'")

        if filters:
            if filters.brand and variant.product.brand.lower() == filters.brand.lower():
                reasons.append(f"Brand: {variant.product.brand}")

            if filters.min_memory and variant.memory_size and variant.memory_size >= filters.min_memory:
                reasons.append(f"Memory: {variant.memory_size}GB (≥{filters.min_memory}GB)")

            if filters.storage_type and variant.storage_type:
                if filters.storage_type.lower() in variant.storage_type.lower():
                    reasons.append(f"Storage type: {variant.storage_type}")

        return reasons

    async def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get intelligent search suggestions based on partial query"""
        suggestions = []
        query_lower = partial_query.lower()

        # 1. Quick completions (complete partial words)
        quick_completions = []

        # Brand completions
        if any(brand.startswith(query_lower) for brand in ['hp', 'lenovo', 'dell']):
            brands = self.db.query(Product.brand).filter(
                Product.brand.ilike(f"{partial_query}%")
            ).distinct().limit(2).all()
            quick_completions.extend([b.brand for b in brands if b.brand])

        # Processor family completions
        if any(proc.startswith(query_lower) for proc in ['intel', 'amd', 'ryzen', 'core']):
            processors = self.db.query(Variant.processor_family).filter(
                Variant.processor_family.ilike(f"%{partial_query}%")
            ).distinct().limit(2).all()
            quick_completions.extend([p.processor_family for p in processors if p.processor_family])

        # 2. Popular product models (extract model numbers)
        model_suggestions = []
        if len(partial_query) >= 2:
            # Get products matching the query and extract model info
            products = self.db.query(Product.product_name, Product.brand).filter(
                Product.product_name.ilike(f"%{partial_query}%")
            ).limit(10).all()

            seen_models = set()
            for product in products:
                # Extract model series (like "G11", "ProBook", "EliteBook")
                words = product.product_name.split()
                for word in words:
                    if (len(word) >= 3 and
                        (word.lower().startswith(query_lower) or query_lower in word.lower()) and
                        word not in seen_models and
                        word.lower() not in ['inch', 'notebook', 'pc', 'laptop', 'with']):
                        model_suggestions.append(f"{product.brand} {word}")
                        seen_models.add(word)
                        if len(model_suggestions) >= 2:
                            break

        # 3. Feature suggestions
        feature_suggestions = []
        feature_keywords = {
            'touch': 'Touchscreen laptops',
            'gaming': 'Gaming laptops',
            'business': 'Business laptops',
            'light': 'Lightweight laptops',
            'portable': 'Portable laptops',
            '14': '14 inch laptops',
            '15': '15 inch laptops',
            '16': '16 inch laptops'
        }

        for keyword, suggestion in feature_keywords.items():
            if keyword in query_lower:
                feature_suggestions.append(suggestion)

        # 4. Memory and storage suggestions
        spec_suggestions = []
        if any(spec in query_lower for spec in ['8gb', '16gb', '32gb', 'ssd', '512', '1tb']):
            if '8gb' in query_lower or '8 gb' in query_lower:
                spec_suggestions.append('8GB RAM laptops')
            if '16gb' in query_lower or '16 gb' in query_lower:
                spec_suggestions.append('16GB RAM laptops')
            if 'ssd' in query_lower:
                spec_suggestions.append('SSD laptops')

        # Combine suggestions in priority order
        suggestions.extend(quick_completions[:2])
        suggestions.extend(model_suggestions[:2])
        suggestions.extend(feature_suggestions[:1])
        suggestions.extend(spec_suggestions[:1])

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion and suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        return unique_suggestions[:limit]

    async def semantic_search(self, query: str, limit: int = 10, include_similar: bool = True) -> List[Dict]:
        """Perform semantic search using natural language processing"""

        # For now, implement a rule-based semantic search
        # In production, this would use embeddings/vector search

        results = []
        query_lower = query.lower()

        # Enhanced keyword mapping for semantic understanding
        semantic_keywords = {
            # Performance keywords
            'fast': ['intel', 'amd ryzen 7', 'amd ryzen 5', 'ssd'],
            'powerful': ['intel core i7', 'amd ryzen 7', '16gb', '32gb'],
            'performance': ['intel', 'amd ryzen', 'ssd', '16gb'],
            'speed': ['ssd', 'intel', 'amd ryzen'],

            # Usage patterns
            'gaming': ['amd ryzen 7', 'intel core i7', '16gb', '32gb', 'dedicated'],
            'work': ['intel', 'amd ryzen 5', '8gb', '16gb', 'ssd'],
            'business': ['intel', 'amd ryzen', 'pro', '8gb', '16gb'],
            'office': ['intel', 'amd ryzen', '8gb', 'ssd'],
            'student': ['amd ryzen 3', 'intel core i5', '8gb', 'budget'],

            # Form factors
            'portable': ['14', '13', 'light', 'thin'],
            'lightweight': ['14', '13', 'light'],
            'compact': ['14', '13'],
            'large': ['16', '17'],
            'big': ['16', '17'],

            # Features
            'touchscreen': ['touch'],
            'security': ['fingerprint', 'pro', 'elite'],
            'professional': ['pro', 'elite', 'business']
        }

        # Extract semantic intent
        search_terms = []
        for keyword, expansions in semantic_keywords.items():
            if keyword in query_lower:
                search_terms.extend(expansions)

        # If no semantic matches, fall back to the original query
        if not search_terms:
            search_terms = [query]

        # Build dynamic filter based on semantic understanding
        filters = SearchFilters()

        # Apply semantic filters
        for term in search_terms:
            if term in ['intel', 'amd']:
                if not filters.processor_family:
                    filters.processor_family = term
            elif 'gb' in term and term.replace('gb', '').isdigit():
                memory_size = int(term.replace('gb', ''))
                if not filters.min_memory or memory_size > filters.min_memory:
                    filters.min_memory = memory_size
            elif term == 'ssd':
                filters.storage_type = 'SSD'
            # Note: display_size filter was removed, but we can still use it for semantic scoring

        # Perform the enhanced search
        enhanced_results = await self.search(
            query=query,
            filters=filters,
            limit=limit * 2 if include_similar else limit  # Get more results if including similar
        )

        # Convert to semantic search format
        for result in enhanced_results[:limit]:
            semantic_result = {
                "variant": {
                    "id": str(result.variant.id),
                    "product_name": result.variant.product_name,
                    "brand": result.variant.brand,
                    "processor": result.variant.processor,
                    "memory": result.variant.memory,
                    "storage": result.variant.storage,
                    "price": str(result.variant.price),
                    "display_size": str(result.variant.display_size) if result.variant.display_size else None
                },
                "relevance_score": result.relevance_score,
                "semantic_similarity": self._calculate_semantic_similarity(query, result.variant),
                "match_reasons": result.match_reasons
            }
            results.append(semantic_result)

        return results

    def _calculate_semantic_similarity(self, query: str, variant) -> float:
        """Calculate semantic similarity score between query and variant"""
        score = 0.0
        query_lower = query.lower()

        # Check brand match
        if variant.brand and variant.brand.lower() in query_lower:
            score += 0.3

        # Check processor match
        if variant.processor and any(proc in variant.processor.lower() for proc in query_lower.split()):
            score += 0.2

        # Check memory relevance
        if variant.memory_size:
            if 'gaming' in query_lower and variant.memory_size >= 16:
                score += 0.2
            elif 'work' in query_lower and variant.memory_size >= 8:
                score += 0.15

        # Check storage type
        if variant.storage_type and 'ssd' in variant.storage_type.lower() and ('fast' in query_lower or 'performance' in query_lower):
            score += 0.15

        # Check display size for portability queries
        if variant.display_size:
            if 'portable' in query_lower and variant.display_size <= 14:
                score += 0.15
            elif 'large' in query_lower and variant.display_size >= 16:
                score += 0.15

        return min(score, 1.0)  # Cap at 1.0

    async def analyze_search_intent(self, query: str) -> Dict:
        """Analyze search intent from natural language query"""

        query_lower = query.lower()
        intent = {
            "primary_intent": "product_search",
            "use_case": None,
            "performance_level": None,
            "price_sensitivity": None,
            "form_factor_preference": None,
            "confidence": 0.8
        }

        # Detect use case intent
        if any(word in query_lower for word in ['gaming', 'game', 'games']):
            intent["use_case"] = "gaming"
            intent["performance_level"] = "high"
        elif any(word in query_lower for word in ['work', 'office', 'business', 'professional']):
            intent["use_case"] = "business"
            intent["performance_level"] = "medium"
        elif any(word in query_lower for word in ['student', 'school', 'study']):
            intent["use_case"] = "education"
            intent["performance_level"] = "basic"
        elif any(word in query_lower for word in ['creative', 'design', 'video', 'photo']):
            intent["use_case"] = "creative"
            intent["performance_level"] = "high"

        # Detect performance intent
        if any(word in query_lower for word in ['fast', 'powerful', 'high-performance', 'speed']):
            intent["performance_level"] = "high"
        elif any(word in query_lower for word in ['basic', 'simple', 'budget']):
            intent["performance_level"] = "basic"

        # Detect price sensitivity
        if any(word in query_lower for word in ['cheap', 'budget', 'affordable', 'low-cost']):
            intent["price_sensitivity"] = "high"
        elif any(word in query_lower for word in ['premium', 'expensive', 'high-end']):
            intent["price_sensitivity"] = "low"

        # Detect form factor preference
        if any(word in query_lower for word in ['portable', 'lightweight', 'compact', 'small']):
            intent["form_factor_preference"] = "portable"
        elif any(word in query_lower for word in ['large', 'big', 'wide']):
            intent["form_factor_preference"] = "large"

        return intent

    async def intelligent_search(
        self,
        query: str,
        user_context: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        use_case: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Perform intelligent search with context awareness and smart filtering"""

        # Start with base filters
        filters = SearchFilters()

        # Apply budget constraints if provided
        if budget_min and budget_min > 0:
            filters.min_price = budget_min
        if budget_max and budget_max > 0:
            filters.max_price = budget_max

        # Intelligent use case analysis
        use_case_lower = (use_case or "").lower() if use_case else ""
        user_context_lower = (user_context or "").lower() if user_context else ""
        query_lower = query.lower()

        # Combine all text for comprehensive analysis
        combined_text = f"{query_lower} {use_case_lower} {user_context_lower}"

        # Gaming use case intelligence
        if any(keyword in combined_text for keyword in ['gaming', 'games', 'game', 'gamer']):
            # Prefer high-performance specs for gaming
            if not filters.min_memory or filters.min_memory < 16:
                filters.min_memory = 16  # Gaming needs at least 16GB
            filters.storage_type = 'SSD'  # SSD is crucial for gaming
            if 'amd' not in query_lower and 'intel' not in query_lower:
                # Prefer AMD for gaming if no specific preference
                filters.processor_family = 'AMD'

        # Business/Work use case intelligence
        elif any(keyword in combined_text for keyword in ['business', 'work', 'office', 'professional', 'productivity']):
            if not filters.min_memory or filters.min_memory < 8:
                filters.min_memory = 8  # Business needs at least 8GB
            filters.storage_type = 'SSD'  # Fast storage for productivity
            # Prefer Intel for business unless AMD specifically mentioned
            if 'amd' not in query_lower:
                filters.processor_family = 'Intel'

        # Student/Budget use case intelligence
        elif any(keyword in combined_text for keyword in ['student', 'school', 'study', 'budget', 'cheap', 'affordable']):
            if not filters.min_memory:
                filters.min_memory = 8  # Students need at least 8GB
            # Don't restrict processor family for budget builds
            filters.storage_type = 'SSD'  # Still prefer SSD for better experience

        # Creative use case intelligence
        elif any(keyword in combined_text for keyword in ['design', 'creative', 'video', 'photo', 'editing']):
            if not filters.min_memory or filters.min_memory < 16:
                filters.min_memory = 16  # Creative work needs memory
            filters.storage_type = 'SSD'  # Fast storage for large files

        # Extract brand preference from query
        if any(brand in query_lower for brand in ['hp', 'hewlett']):
            filters.brand = 'HP'
        elif any(brand in query_lower for brand in ['lenovo']):
            filters.brand = 'Lenovo'
        elif any(brand in query_lower for brand in ['dell']):
            filters.brand = 'Dell'

        # Intelligent processor preference based on context
        if not filters.processor_family:
            if any(keyword in combined_text for keyword in ['fast', 'performance', 'powerful']):
                # Prefer high-performance processors
                filters.processor_family = 'AMD Ryzen 7' if 'amd' in combined_text else 'Intel'
            elif any(keyword in combined_text for keyword in ['efficiency', 'battery', 'portable']):
                # Prefer efficient processors
                filters.processor_family = 'Intel'

        # Perform the enhanced search
        results = await self.search(
            query=query,
            filters=filters,
            limit=limit * 2  # Get more results for intelligent ranking
        )

        # Intelligent ranking based on context
        ranked_results = self._intelligent_ranking(results, use_case, user_context, budget_min, budget_max)

        # Convert to intelligent search format
        intelligent_results = []
        for i, result in enumerate(ranked_results[:limit]):
            intelligent_result = {
                "variant": {
                    "id": str(result.variant.id),
                    "product_name": result.variant.product_name,
                    "brand": result.variant.brand,
                    "processor": result.variant.processor,
                    "memory": result.variant.memory,
                    "storage": result.variant.storage,
                    "price": str(result.variant.price),
                    "display_size": str(result.variant.display_size) if result.variant.display_size else None,
                    "availability": result.variant.availability
                },
                "relevance_score": result.relevance_score,
                "intelligence_score": self._calculate_intelligence_score(result.variant, use_case, user_context),
                "ranking_position": i + 1,
                "match_reasons": result.match_reasons,
                "context_match": self._analyze_context_match(result.variant, use_case, user_context),
                "value_assessment": self._assess_value(result.variant, budget_min, budget_max)
            }
            intelligent_results.append(intelligent_result)

        return intelligent_results

    def _intelligent_ranking(self, results, use_case: Optional[str], user_context: Optional[str],
                           budget_min: Optional[float], budget_max: Optional[float]) -> List:
        """Apply intelligent ranking based on context and preferences"""

        def intelligence_score(result):
            score = result.relevance_score or 0
            variant = result.variant

            # Use case specific scoring
            if use_case:
                use_case_lower = use_case.lower()
                if 'gaming' in use_case_lower:
                    # Prefer high memory and good processors for gaming
                    if variant.memory_size and variant.memory_size >= 16:
                        score += 0.3
                    if variant.processor and any(proc in variant.processor.lower()
                                               for proc in ['ryzen 7', 'core i7', 'ultra 7']):
                        score += 0.2
                elif 'business' in use_case_lower:
                    # Prefer reliable specs and Pro models
                    if variant.product_name and 'pro' in variant.product_name.lower():
                        score += 0.2
                    if variant.memory_size and 8 <= variant.memory_size <= 16:
                        score += 0.15

            # Budget scoring
            if budget_min and budget_max and variant.price:
                price = float(variant.price)
                if budget_min <= price <= budget_max:
                    # Prefer products in the middle of budget range
                    budget_mid = (budget_min + budget_max) / 2
                    budget_range = budget_max - budget_min
                    distance_from_mid = abs(price - budget_mid) / budget_range
                    score += 0.2 * (1 - distance_from_mid)

            # Value scoring (performance per dollar)
            if variant.price and float(variant.price) > 0:
                value_score = 0
                if variant.memory_size:
                    value_score += variant.memory_size * 50  # Memory value
                if variant.storage_size:
                    value_score += variant.storage_size * 2  # Storage value
                if variant.storage_type and 'ssd' in variant.storage_type.lower():
                    value_score += 500  # SSD bonus

                if value_score > 0:
                    value_per_dollar = value_score / float(variant.price)
                    score += min(value_per_dollar * 0.001, 0.2)  # Cap value bonus

            return score

        return sorted(results, key=intelligence_score, reverse=True)

    def _calculate_intelligence_score(self, variant, use_case: Optional[str], user_context: Optional[str]) -> float:
        """Calculate AI-powered intelligence score for context matching"""
        score = 0.0

        if use_case:
            use_case_lower = use_case.lower()

            if 'gaming' in use_case_lower:
                # Gaming intelligence
                if variant.memory_size and variant.memory_size >= 16:
                    score += 0.4
                if variant.processor and any(proc in variant.processor.lower()
                                           for proc in ['ryzen 7', 'ryzen 5', 'core i7', 'ultra 7']):
                    score += 0.3
                if variant.storage_type and 'ssd' in variant.storage_type.lower():
                    score += 0.3

            elif 'business' in use_case_lower:
                # Business intelligence
                if variant.product_name and any(term in variant.product_name.lower()
                                              for term in ['pro', 'elite', 'business']):
                    score += 0.4
                if variant.memory_size and 8 <= variant.memory_size <= 16:
                    score += 0.3
                if variant.processor and 'intel' in variant.processor.lower():
                    score += 0.3

        # User context analysis
        if user_context:
            context_lower = user_context.lower()
            if variant.brand and variant.brand.lower() in context_lower:
                score += 0.2
            if variant.processor and any(proc in context_lower for proc in ['amd', 'intel', 'ryzen', 'core']):
                score += 0.1

        return min(score, 1.0)

    def _analyze_context_match(self, variant, use_case: Optional[str], user_context: Optional[str]) -> List[str]:
        """Analyze how well the variant matches the user's context"""
        matches = []

        if use_case:
            use_case_lower = use_case.lower()
            if 'gaming' in use_case_lower:
                if variant.memory_size and variant.memory_size >= 16:
                    matches.append(f"Excellent for gaming with {variant.memory_size}GB RAM")
                if variant.storage_type and 'ssd' in variant.storage_type.lower():
                    matches.append("Fast SSD storage for quick game loading")

            elif 'business' in use_case_lower:
                if variant.product_name and 'pro' in variant.product_name.lower():
                    matches.append("Professional business laptop line")
                if variant.memory_size and variant.memory_size >= 8:
                    matches.append("Sufficient memory for business applications")

        if user_context:
            context_lower = user_context.lower()
            if variant.brand and variant.brand.lower() in context_lower:
                matches.append(f"Matches your {variant.brand} brand preference")

        return matches

    def _assess_value(self, variant, budget_min: Optional[float], budget_max: Optional[float]) -> Dict:
        """Assess the value proposition of the variant"""
        assessment = {
            "value_rating": "unknown",
            "price_position": "unknown",
            "value_highlights": []
        }

        if not variant.price or float(variant.price) == 0:
            return assessment

        price = float(variant.price)

        # Budget position assessment
        if budget_min and budget_max:
            if price < budget_min:
                assessment["price_position"] = "below_budget"
                assessment["value_highlights"].append(f"${budget_min - price:.0f} under your minimum budget")
            elif price > budget_max:
                assessment["price_position"] = "above_budget"
                assessment["value_highlights"].append(f"${price - budget_max:.0f} over your maximum budget")
            else:
                budget_range = budget_max - budget_min
                position = (price - budget_min) / budget_range
                if position < 0.3:
                    assessment["price_position"] = "budget_friendly"
                elif position > 0.7:
                    assessment["price_position"] = "premium_range"
                else:
                    assessment["price_position"] = "mid_range"

        # Value assessment based on specs
        value_score = 0
        if variant.memory_size:
            value_score += variant.memory_size * 10
        if variant.storage_size:
            value_score += variant.storage_size * 2
        if variant.storage_type and 'ssd' in variant.storage_type.lower():
            value_score += 200

        if value_score > 0 and price > 0:
            value_per_dollar = value_score / price
            if value_per_dollar > 0.5:
                assessment["value_rating"] = "excellent"
                assessment["value_highlights"].append("Excellent performance per dollar")
            elif value_per_dollar > 0.3:
                assessment["value_rating"] = "good"
                assessment["value_highlights"].append("Good value for the specs")
            else:
                assessment["value_rating"] = "fair"

        return assessment

    async def get_search_insights(self, query: str, results: List[Dict]) -> List[str]:
        """Generate intelligent insights about the search results"""
        insights = []

        if not results:
            insights.append("No products found matching your criteria. Try broadening your search.")
            return insights

        # Price analysis
        prices = [float(r["variant"]["price"]) for r in results if r["variant"]["price"] and float(r["variant"]["price"]) > 0]
        if prices:
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)

            insights.append(f"Found {len(results)} options ranging from ${min_price:.0f} to ${max_price:.0f}")
            insights.append(f"Average price in results: ${avg_price:.0f}")

        # Brand analysis
        brands = [r["variant"]["brand"] for r in results if r["variant"]["brand"]]
        if brands:
            brand_counts = {}
            for brand in brands:
                brand_counts[brand] = brand_counts.get(brand, 0) + 1

            top_brand = max(brand_counts.items(), key=lambda x: x[1])
            insights.append(f"Most common brand in results: {top_brand[0]} ({top_brand[1]} models)")

        # Memory analysis
        memory_sizes = [int(r["variant"]["memory"].split()[0]) for r in results
                       if r["variant"]["memory"] and r["variant"]["memory"].split()[0].isdigit()]
        if memory_sizes:
            avg_memory = sum(memory_sizes) / len(memory_sizes)
            insights.append(f"Average memory: {avg_memory:.0f}GB")

        # Performance insights based on query
        query_lower = query.lower()
        if 'gaming' in query_lower:
            high_mem_count = sum(1 for mem in memory_sizes if mem >= 16)
            insights.append(f"{high_mem_count} out of {len(results)} models have 16GB+ RAM suitable for gaming")

        return insights[:5]  # Limit to top 5 insights

    async def get_related_searches(self, query: str) -> List[str]:
        """Generate related search suggestions based on the current query"""
        related = []
        query_lower = query.lower()

        # Brand-based related searches
        if 'hp' in query_lower:
            related.extend(['HP ProBook series', 'HP EliteBook professional', 'HP gaming laptops'])
        elif 'lenovo' in query_lower:
            related.extend(['Lenovo ThinkPad business', 'Lenovo IdeaPad series', 'Lenovo Legion gaming'])
        elif 'dell' in query_lower:
            related.extend(['Dell Latitude business', 'Dell XPS premium', 'Dell Inspiron series'])

        # Use case related searches
        if any(term in query_lower for term in ['gaming', 'game']):
            related.extend(['High-performance gaming laptops', 'AMD Ryzen gaming laptops', '16GB gaming laptops'])
        elif any(term in query_lower for term in ['business', 'work']):
            related.extend(['Business laptops with SSD', 'Professional mobile workstations', 'Enterprise security laptops'])
        elif any(term in query_lower for term in ['student', 'budget']):
            related.extend(['Budget laptops under $1000', 'Student laptop deals', 'Best value laptops'])

        # Spec-based related searches
        if 'laptop' in query_lower and len(related) < 3:
            related.extend(['SSD laptops', '16GB RAM laptops', 'Touchscreen laptops'])

        # Performance related searches
        if any(term in query_lower for term in ['fast', 'performance']):
            related.extend(['High-performance processors', 'Fast SSD storage', 'Multi-core processors'])

        return related[:5]  # Limit to 5 related searches

    async def get_filter_options(self) -> Dict:
        """Get available filter options based on current data"""
        brands = self.db.query(Product.brand).distinct().all()
        processor_families = self.db.query(Variant.processor_family).distinct().all()
        memory_sizes = self.db.query(Variant.memory_size).distinct().all()
        storage_types = self.db.query(Variant.storage_type).distinct().all()

        # Get price range
        min_price = self.db.query(func.min(Variant.price)).scalar() or 0
        max_price = self.db.query(func.max(Variant.price)).scalar() or 5000

        return {
            "brands": [b.brand for b in brands if b.brand],
            "processor_families": [pf.processor_family for pf in processor_families if pf.processor_family],
            "memory_sizes": sorted([ms.memory_size for ms in memory_sizes if ms.memory_size]),
            "storage_types": [st.storage_type for st in storage_types if st.storage_type],
            "price_range": {
                "min": float(min_price),
                "max": float(max_price)
            }
        }