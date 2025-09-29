"""
Pinecone Vector Database Service for enhanced product search and retrieval
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
import json
from datetime import datetime

# Core imports
from app.core.config import settings

# Pinecone imports
try:
    import pinecone
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None
    Pinecone = None
    ServerlessSpec = None

# Gemini embeddings
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class PineconeService:
    """Service for interacting with Pinecone vector database"""

    def __init__(self):
        self.pc = None
        self.index = None
        self.genai_client = None
        self.initialized = False

        if PINECONE_AVAILABLE and settings.PINECONE_API_KEY:
            self._initialize_pinecone()
        else:
            logger.warning("Pinecone not available or API key not configured")

        if GEMINI_AVAILABLE and settings.GEMINI_API_KEY:
            self._initialize_gemini_embeddings()
        else:
            logger.warning("Gemini embeddings not available")

    def _initialize_pinecone(self):
        """Initialize Pinecone client and index"""
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

            # Check if index exists, create if not
            index_name = settings.PINECONE_INDEX

            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                # Gemini embeddings have 768 dimensions
                self.pc.create_index(
                    name=index_name,
                    dimension=768,  # Gemini embedding dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )

            # Connect to index
            self.index = self.pc.Index(index_name)
            self.initialized = True
            logger.info(f"Successfully connected to Pinecone index: {index_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.initialized = False

    def _initialize_gemini_embeddings(self):
        """Initialize Gemini embeddings"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.genai_client = True  # Just a flag to indicate it's configured
            logger.info("Initialized Gemini embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embeddings: {e}")
            self.genai_client = None

    def is_available(self) -> bool:
        """Check if Pinecone service is available"""
        return self.initialized and self.genai_client is not None

    def get_embedding(self, text: str, task_type: str = "retrieval_document") -> Optional[List[float]]:
        """Generate embedding for text using Gemini"""
        if not self.genai_client:
            return None

        try:
            # Use Gemini's embedding model
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Failed to generate Gemini embedding: {e}")
            return None

    def analyze_and_improve_query(self, original_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user query and improve it for better vector search
        """
        improved_queries = []
        search_strategies = []

        query_lower = original_query.lower()

        # Extract key information from query
        extracted_info = self._extract_query_features(original_query, context)

        # Strategy 1: Original query with context enhancement
        if context:
            budget = context.get('budget')
            use_case = context.get('use_case')

            enhanced_query = original_query
            if budget:
                enhanced_query += f" budget under ${budget}"
            if use_case:
                enhanced_query += f" for {use_case}"

            improved_queries.append(enhanced_query)
            search_strategies.append("context_enhanced")

        # Strategy 2: Feature-focused queries
        if extracted_info.get('features'):
            feature_query = " ".join(extracted_info['features']) + " laptop computer"
            improved_queries.append(feature_query)
            search_strategies.append("feature_focused")

        # Strategy 3: Use case optimization
        if extracted_info.get('use_case'):
            use_case_query = f"{extracted_info['use_case']} laptop professional computer"
            improved_queries.append(use_case_query)
            search_strategies.append("use_case_optimized")

        # Strategy 4: Brand and spec focused
        if extracted_info.get('brands') or extracted_info.get('specs'):
            spec_parts = []
            if extracted_info.get('brands'):
                spec_parts.extend(extracted_info['brands'])
            if extracted_info.get('specs'):
                spec_parts.extend(extracted_info['specs'])
            spec_parts.append("laptop computer")

            spec_query = " ".join(spec_parts)
            improved_queries.append(spec_query)
            search_strategies.append("brand_spec_focused")

        # Strategy 5: Semantic expansion
        semantic_expansion = self._get_semantic_expansion(original_query)
        if semantic_expansion:
            improved_queries.append(semantic_expansion)
            search_strategies.append("semantic_expansion")

        # If no improvements, use original
        if not improved_queries:
            improved_queries.append(original_query)
            search_strategies.append("original")

        return {
            "original_query": original_query,
            "improved_queries": improved_queries,
            "search_strategies": search_strategies,
            "extracted_features": extracted_info,
            "query_intent": self._classify_query_intent(original_query)
        }

    def _extract_query_features(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract features from user query"""
        query_lower = query.lower()
        features = {
            'brands': [],
            'specs': [],
            'features': [],
            'use_case': None,
            'price_indicators': [],
            'performance_level': None
        }

        # Brand extraction
        brands = ['hp', 'lenovo', 'dell', 'asus', 'acer', 'msi', 'apple', 'microsoft', 'samsung']
        for brand in brands:
            if brand in query_lower:
                features['brands'].append(brand)

        # Specs extraction
        spec_patterns = {
            'memory': ['16gb', '32gb', '8gb', '4gb', 'ram', 'memory'],
            'storage': ['ssd', 'nvme', '512gb', '1tb', '256gb', 'storage'],
            'processor': ['intel', 'amd', 'ryzen', 'core', 'i5', 'i7', 'i9', 'processor', 'cpu'],
            'display': ['4k', '2k', 'fhd', 'uhd', 'touchscreen', 'touch', '14 inch', '15 inch'],
            'graphics': ['rtx', 'gtx', 'graphics', 'gpu', 'nvidia', 'radeon']
        }

        for category, patterns in spec_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    features['specs'].append(pattern)

        # Features extraction
        feature_keywords = ['lightweight', 'portable', 'gaming', 'business', 'professional',
                           'touchscreen', 'convertible', '2-in-1', 'ultrabook', 'workstation']
        for keyword in feature_keywords:
            if keyword in query_lower:
                features['features'].append(keyword)

        # Use case detection
        use_cases = {
            'gaming': ['gaming', 'game', 'gamer', 'games'],
            'business': ['business', 'office', 'work', 'professional', 'corporate'],
            'programming': ['programming', 'development', 'coding', 'developer', 'software'],
            'student': ['student', 'school', 'education', 'study', 'college'],
            'creative': ['creative', 'design', 'photo', 'video', 'content', 'editing'],
            'travel': ['travel', 'portable', 'mobile', 'lightweight']
        }

        for use_case, keywords in use_cases.items():
            if any(keyword in query_lower for keyword in keywords):
                features['use_case'] = use_case
                break

        # Price indicators
        price_terms = ['budget', 'cheap', 'affordable', 'expensive', 'premium', 'high-end', 'under', 'below']
        for term in price_terms:
            if term in query_lower:
                features['price_indicators'].append(term)

        return features

    def _get_semantic_expansion(self, query: str) -> Optional[str]:
        """Generate semantic expansion of query"""
        query_lower = query.lower()

        # Semantic expansions for common terms
        expansions = {
            'laptop': 'notebook computer portable pc',
            'fast': 'high performance quick speed efficient',
            'gaming': 'gaming graphics gpu rtx gtx performance',
            'business': 'professional office work corporate enterprise',
            'portable': 'lightweight mobile travel compact',
            'budget': 'affordable inexpensive cost-effective value',
            'premium': 'high-end expensive top-tier flagship'
        }

        expanded_terms = []
        for term, expansion in expansions.items():
            if term in query_lower:
                expanded_terms.append(expansion)

        if expanded_terms:
            return query + " " + " ".join(expanded_terms)

        return None

    def _classify_query_intent(self, query: str) -> str:
        """Classify the intent of the user query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['recommend', 'suggest', 'best', 'good']):
            return 'recommendation'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            return 'comparison'
        elif any(word in query_lower for word in ['find', 'search', 'show', 'list']):
            return 'search'
        elif any(word in query_lower for word in ['price', 'cost', 'deal', 'discount']):
            return 'pricing'
        elif any(word in query_lower for word in ['spec', 'specification', 'detail', 'feature']):
            return 'specification'
        else:
            return 'general'

    async def enhanced_vector_search(self, query_analysis: Dict[str, Any], limit: int = 10, include_pdfs: bool = True) -> List[Dict[str, Any]]:
        """
        Perform enhanced vector search using multiple strategies
        """
        if not self.is_available():
            logger.warning("Pinecone service not available for vector search")
            return []

        all_results = []
        query_strategies = query_analysis.get('search_strategies', ['original'])
        improved_queries = query_analysis.get('improved_queries', [query_analysis.get('original_query', '')])

        # Execute multiple search strategies
        for strategy, query in zip(query_strategies, improved_queries):
            try:
                # Search products
                results = await self._vector_search_single(query, limit // len(improved_queries) + 1)

                # Add strategy metadata to results
                for result in results:
                    result['search_strategy'] = strategy
                    result['query_used'] = query

                all_results.extend(results)

                # Also search PDF chunks if requested
                if include_pdfs:
                    pdf_results = await self.search_pdf_context(query, limit=3)
                    for pdf_result in pdf_results:
                        pdf_result['search_strategy'] = f"{strategy}_pdf"
                        pdf_result['query_used'] = query
                        pdf_result['result_type'] = 'pdf_chunk'
                    all_results.extend(pdf_results)

            except Exception as e:
                logger.error(f"Vector search failed for strategy {strategy}: {e}")
                continue

        # Deduplicate and rank results
        unique_results = self._deduplicate_and_rank(all_results, query_analysis)

        return unique_results[:limit]

    async def _vector_search_single(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform single vector search"""
        if not self.is_available():
            return []

        try:
            # Generate embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []

            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                include_values=False
            )

            # Format results
            formatted_results = []
            for match in search_results.matches:
                result = {
                    'id': match.id,
                    'score': float(match.score),
                    'metadata': match.metadata or {},
                    'content': match.metadata.get('content', '') if match.metadata else ''
                }
                formatted_results.append(result)

            return formatted_results

        except Exception as e:
            logger.error(f"Single vector search failed: {e}")
            return []

    def _deduplicate_and_rank(self, results: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Deduplicate results and apply intelligent ranking"""
        if not results:
            return []

        # Deduplicate by ID
        seen_ids = set()
        unique_results = []

        for result in results:
            result_id = result.get('id')
            if result_id not in seen_ids:
                seen_ids.add(result_id)
                unique_results.append(result)

        # Apply intelligent ranking based on query intent
        query_intent = query_analysis.get('query_intent', 'general')
        extracted_features = query_analysis.get('extracted_features', {})

        for result in unique_results:
            result['final_score'] = self._calculate_relevance_score(result, query_intent, extracted_features)

        # Sort by final score
        unique_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)

        return unique_results

    def _calculate_relevance_score(self, result: Dict[str, Any], query_intent: str, extracted_features: Dict[str, Any]) -> float:
        """Calculate final relevance score for ranking"""
        base_score = result.get('score', 0)
        metadata = result.get('metadata', {})

        # Boost factors
        boost = 1.0

        # Intent-based boosting
        if query_intent == 'recommendation' and metadata.get('type') == 'product':
            boost += 0.2
        elif query_intent == 'pricing' and 'price' in metadata:
            boost += 0.15

        # Feature matching boost
        if extracted_features.get('brands'):
            product_brand = metadata.get('brand', '').lower()
            if any(brand in product_brand for brand in extracted_features['brands']):
                boost += 0.3

        if extracted_features.get('use_case'):
            product_category = metadata.get('category', '').lower()
            if extracted_features['use_case'] in product_category:
                boost += 0.25

        # Strategy boost (some strategies are more reliable)
        strategy = result.get('search_strategy', 'original')
        strategy_weights = {
            'context_enhanced': 1.2,
            'feature_focused': 1.1,
            'use_case_optimized': 1.15,
            'brand_spec_focused': 1.1,
            'semantic_expansion': 1.05,
            'original': 1.0
        }
        boost *= strategy_weights.get(strategy, 1.0)

        return base_score * boost

    async def upsert_pdf_chunks(self, pdf_chunks: List[Dict[str, Any]], source_metadata: Dict[str, Any] = None) -> bool:
        """Upsert PDF document chunks to Pinecone with metadata"""
        if not self.is_available():
            logger.warning("Pinecone service not available for PDF upserting")
            return False

        try:
            vectors_to_upsert = []

            for chunk in pdf_chunks:
                # Create content for embedding
                content = chunk.get('content', '')
                if not content:
                    continue

                # Generate embedding
                embedding = self.get_embedding(content)
                if not embedding:
                    continue

                # Prepare metadata
                metadata = {
                    'content': content[:1000],  # Truncate for metadata storage
                    'full_content': content,
                    'source': chunk.get('source', 'unknown'),
                    'page': chunk.get('page', 0),
                    'chunk_id': chunk.get('chunk_id', ''),
                    'type': 'pdf_chunk',
                    'created_at': datetime.utcnow().isoformat()
                }

                # Add PDF specification link if available
                if source_metadata:
                    metadata['pdf_url'] = source_metadata.get('pdf_url', '')
                    metadata['product_name'] = source_metadata.get('product_name', '')
                    metadata['brand'] = source_metadata.get('brand', '')

                # Prepare vector for upsert
                vector_data = {
                    'id': chunk.get('chunk_id', f"chunk_{datetime.utcnow().timestamp()}"),
                    'values': embedding,
                    'metadata': metadata
                }

                vectors_to_upsert.append(vector_data)

            # Batch upsert
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"Successfully upserted {len(vectors_to_upsert)} PDF chunks to Pinecone")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to upsert PDF chunks to Pinecone: {e}")
            return False

    async def search_pdf_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant PDF chunks based on query"""
        if not self.is_available():
            logger.warning("Pinecone service not available for PDF search")
            return []

        try:
            # Generate embedding for query
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []

            # Search in Pinecone with filter for PDF chunks
            search_results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True,
                include_values=False,
                filter={"type": "pdf_chunk"}
            )

            # Format results
            pdf_contexts = []
            for match in search_results.matches:
                context = {
                    'chunk_id': match.id,
                    'score': float(match.score),
                    'content': match.metadata.get('full_content', match.metadata.get('content', '')),
                    'source': match.metadata.get('source', ''),
                    'page': match.metadata.get('page', 0),
                    'pdf_url': match.metadata.get('pdf_url', ''),
                    'product_name': match.metadata.get('product_name', ''),
                    'relevance': 'high' if match.score > 0.8 else 'medium' if match.score > 0.6 else 'low'
                }
                pdf_contexts.append(context)

            return pdf_contexts

        except Exception as e:
            logger.error(f"PDF context search failed: {e}")
            return []

    async def upsert_product_vectors(self, products_data: List[Dict[str, Any]]) -> bool:
        """Upsert product vectors to Pinecone"""
        if not self.is_available():
            logger.warning("Pinecone service not available for upserting")
            return False

        try:
            vectors_to_upsert = []

            for product in products_data:
                # Create content for embedding
                content = self._create_product_content(product)

                # Generate embedding
                embedding = self.get_embedding(content)
                if not embedding:
                    continue

                # Prepare vector for upsert
                vector_data = {
                    'id': product.get('id', str(product.get('variant_id', ''))),
                    'values': embedding,
                    'metadata': {
                        'content': content,
                        'product_name': product.get('product_name', ''),
                        'brand': product.get('brand', ''),
                        'price': product.get('price', 0),
                        'type': 'product',
                        'category': product.get('category', ''),
                        'created_at': datetime.utcnow().isoformat(),
                        **product.get('metadata', {})
                    }
                }

                vectors_to_upsert.append(vector_data)

            # Batch upsert
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                logger.info(f"Successfully upserted {len(vectors_to_upsert)} vectors to Pinecone")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to upsert vectors to Pinecone: {e}")
            return False

    def _create_product_content(self, product: Dict[str, Any]) -> str:
        """Create searchable content from product data"""
        content_parts = []

        # Basic product info
        if product.get('product_name'):
            content_parts.append(f"Product: {product['product_name']}")

        if product.get('brand'):
            content_parts.append(f"Brand: {product['brand']}")

        if product.get('model_family'):
            content_parts.append(f"Model: {product['model_family']}")

        # Specifications
        specs = ['processor', 'memory', 'storage', 'display', 'graphics']
        for spec in specs:
            if product.get(spec):
                content_parts.append(f"{spec.title()}: {product[spec]}")

        # Price and availability
        if product.get('price'):
            content_parts.append(f"Price: ${product['price']}")

        if product.get('availability'):
            content_parts.append(f"Availability: {product['availability']}")

        # Features
        if product.get('features'):
            features_text = " ".join(product['features'])
            content_parts.append(f"Features: {features_text}")

        # Category and use case
        if product.get('category'):
            content_parts.append(f"Category: {product['category']}")

        return " | ".join(content_parts)

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        if not self.is_available():
            return {"available": False, "error": "Pinecone not available"}

        try:
            stats = self.index.describe_index_stats()
            return {
                "available": True,
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"available": False, "error": str(e)}


# Global instance
pinecone_service = PineconeService()