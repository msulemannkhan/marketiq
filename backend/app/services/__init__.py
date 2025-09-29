from .data_processor import DataProcessor
from .search_service import SearchService
from .recommendation_engine import RecommendationEngine

# Conditionally import LaptopAssistant only if langchain is available
try:
    from .llm_service import LaptopAssistant
    __all__ = ["DataProcessor", "LaptopAssistant", "SearchService", "RecommendationEngine"]
except ImportError:
    # langchain not available, skip LaptopAssistant
    __all__ = ["DataProcessor", "SearchService", "RecommendationEngine"]