from .product import ProductBase, ProductCreate, ProductResponse, ProductWithVariants, ProductSummary
from .variant import VariantBase, VariantCreate, VariantResponse
from .chat import ChatRequest, ChatResponse
from .search import SearchRequest, SearchResponse
from .product_qa import ProductQABase, ProductQACreate, ProductQAUpdate, ProductQAResponse, ProductQASummary, TrendingQuestionResponse
from .product_offer import ProductOfferBase, ProductOfferCreate, ProductOfferUpdate, ProductOfferResponse, OfferSummary
from .review_analytics import (
    ReviewThemeBase, ReviewThemeCreate, ReviewThemeResponse,
    ReviewAnalyticsBase, ReviewAnalyticsCreate, ReviewAnalyticsResponse,
    ReviewInsights, ReviewTrendAnalysis
)
from .user_preference import (
    UserPreferenceBase, UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    SearchHistoryBase, SearchHistoryCreate, SearchHistoryResponse,
    UserRecommendationBase, UserRecommendationCreate, UserRecommendationResponse,
    PersonalizedRecommendations
)
from .data_sync import (
    DataSyncBase, DataSyncCreate, DataSyncUpdate, DataSyncResponse,
    DataFreshnessBase, DataFreshnessCreate, DataFreshnessUpdate, DataFreshnessResponse,
    DataFreshnessSummary, SyncHistory
)
from .product_config import (
    ProductConfigurationBase, ProductConfigurationCreate, ProductConfigurationUpdate, ProductConfigurationResponse,
    ProductConfigurationDetail, ConfigurationVariantBase, ConfigurationVariantCreate, ConfigurationVariantUpdate,
    ConfigurationVariantResponse, ConfigurationVariantDetail, ConfigurationVariantFilter, ConfigurationVariantSearch,
    CarePackageBase, CarePackageCreate, CarePackageResponse, VariantOfferBase, VariantOfferCreate, VariantOfferResponse,
    PriceSnapshotBase, PriceSnapshotCreate, PriceSnapshotResponse, BulkImportRequest, BulkImportResponse,
    ProductConfigurationStats, ProductConfigurationExport
)
from .recommendations import (
    RecommendationConstraints, RecommendationRequest, ProductRecommendation,
    RecommendationResponse, ComparisonRecommendation, SmartRecommendation
)

__all__ = [
    # Product schemas
    "ProductBase", "ProductCreate", "ProductResponse", "ProductWithVariants", "ProductSummary",
    # Variant schemas
    "VariantBase", "VariantCreate", "VariantResponse",
    # Search schemas
    "SearchRequest", "SearchResponse",
    # Chat schemas
    "ChatRequest", "ChatResponse",
    # Q&A schemas
    "ProductQABase", "ProductQACreate", "ProductQAUpdate", "ProductQAResponse", "ProductQASummary", "TrendingQuestionResponse",
    # Offer schemas
    "ProductOfferBase", "ProductOfferCreate", "ProductOfferUpdate", "ProductOfferResponse", "OfferSummary",
    # Review analytics schemas
    "ReviewThemeBase", "ReviewThemeCreate", "ReviewThemeResponse",
    "ReviewAnalyticsBase", "ReviewAnalyticsCreate", "ReviewAnalyticsResponse",
    "ReviewInsights", "ReviewTrendAnalysis",
    # User preference schemas
    "UserPreferenceBase", "UserPreferenceCreate", "UserPreferenceUpdate", "UserPreferenceResponse",
    "SearchHistoryBase", "SearchHistoryCreate", "SearchHistoryResponse",
    "UserRecommendationBase", "UserRecommendationCreate", "UserRecommendationResponse",
    "PersonalizedRecommendations",
    # Data sync schemas
    "DataSyncBase", "DataSyncCreate", "DataSyncUpdate", "DataSyncResponse",
    "DataFreshnessBase", "DataFreshnessCreate", "DataFreshnessUpdate", "DataFreshnessResponse",
    "DataFreshnessSummary", "SyncHistory",
    # Product configuration schemas
    "ProductConfigurationBase", "ProductConfigurationCreate", "ProductConfigurationUpdate", "ProductConfigurationResponse",
    "ProductConfigurationDetail", "ConfigurationVariantBase", "ConfigurationVariantCreate", "ConfigurationVariantUpdate",
    "ConfigurationVariantResponse", "ConfigurationVariantDetail", "ConfigurationVariantFilter", "ConfigurationVariantSearch",
    "CarePackageBase", "CarePackageCreate", "CarePackageResponse", "VariantOfferBase", "VariantOfferCreate", "VariantOfferResponse",
    "PriceSnapshotBase", "PriceSnapshotCreate", "PriceSnapshotResponse", "BulkImportRequest", "BulkImportResponse",
    "ProductConfigurationStats", "ProductConfigurationExport",
    # Recommendation schemas
    "RecommendationConstraints", "RecommendationRequest", "ProductRecommendation",
    "RecommendationResponse", "ComparisonRecommendation", "SmartRecommendation"
]