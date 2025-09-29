"""
Enhanced CRUD operations for new models
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func

from app.models import (
    ProductQA, ProductOffer, ReviewTheme, ReviewAnalytics,
    UserPreference, SearchHistory, UserRecommendation,
    DataSync, DataFreshness
)
from app.schemas import (
    ProductQACreate, ProductQAUpdate,
    ProductOfferCreate, ProductOfferUpdate,
    ReviewThemeCreate, ReviewAnalyticsCreate,
    UserPreferenceCreate, UserPreferenceUpdate,
    SearchHistoryCreate, UserRecommendationCreate,
    DataSyncCreate, DataSyncUpdate,
    DataFreshnessCreate, DataFreshnessUpdate
)


class ProductQACRUD:
    @staticmethod
    def create(db: Session, qa_data: ProductQACreate) -> ProductQA:
        db_qa = ProductQA(**qa_data.dict())
        db.add(db_qa)
        db.commit()
        db.refresh(db_qa)
        return db_qa

    @staticmethod
    def get_by_product(db: Session, product_id: str, limit: int = 20) -> List[ProductQA]:
        return db.query(ProductQA).filter(
            ProductQA.product_id == product_id
        ).order_by(desc(ProductQA.helpful_count)).limit(limit).all()

    @staticmethod
    def update(db: Session, qa_id: str, qa_update: ProductQAUpdate) -> Optional[ProductQA]:
        db_qa = db.query(ProductQA).filter(ProductQA.id == qa_id).first()
        if db_qa:
            for field, value in qa_update.dict(exclude_unset=True).items():
                setattr(db_qa, field, value)
            db.commit()
            db.refresh(db_qa)
        return db_qa

    @staticmethod
    def delete(db: Session, qa_id: str) -> bool:
        db_qa = db.query(ProductQA).filter(ProductQA.id == qa_id).first()
        if db_qa:
            db.delete(db_qa)
            db.commit()
            return True
        return False


class ProductOfferCRUD:
    @staticmethod
    def create(db: Session, offer_data: ProductOfferCreate) -> ProductOffer:
        db_offer = ProductOffer(**offer_data.dict())
        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer

    @staticmethod
    def get_active_by_product(db: Session, product_id: str) -> List[ProductOffer]:
        return db.query(ProductOffer).filter(
            ProductOffer.product_id == product_id,
            ProductOffer.active == True,
            or_(
                ProductOffer.valid_until.is_(None),
                ProductOffer.valid_until > datetime.utcnow()
            )
        ).all()

    @staticmethod
    def get_by_variant(db: Session, variant_id: str) -> List[ProductOffer]:
        return db.query(ProductOffer).filter(
            ProductOffer.variant_id == variant_id,
            ProductOffer.active == True
        ).all()

    @staticmethod
    def update(db: Session, offer_id: str, offer_update: ProductOfferUpdate) -> Optional[ProductOffer]:
        db_offer = db.query(ProductOffer).filter(ProductOffer.id == offer_id).first()
        if db_offer:
            for field, value in offer_update.dict(exclude_unset=True).items():
                setattr(db_offer, field, value)
            db.commit()
            db.refresh(db_offer)
        return db_offer

    @staticmethod
    def deactivate_expired(db: Session) -> int:
        """Deactivate expired offers"""
        count = db.query(ProductOffer).filter(
            ProductOffer.active == True,
            ProductOffer.valid_until < datetime.utcnow()
        ).update({"active": False})
        db.commit()
        return count


class ReviewThemeCRUD:
    @staticmethod
    def create(db: Session, theme_data: ReviewThemeCreate) -> ReviewTheme:
        db_theme = ReviewTheme(**theme_data.dict())
        db.add(db_theme)
        db.commit()
        db.refresh(db_theme)
        return db_theme

    @staticmethod
    def get_by_product(
        db: Session,
        product_id: str,
        sentiment: Optional[str] = None,
        limit: int = 10
    ) -> List[ReviewTheme]:
        query = db.query(ReviewTheme).filter(ReviewTheme.product_id == product_id)

        if sentiment:
            query = query.filter(ReviewTheme.sentiment == sentiment)

        return query.order_by(desc(ReviewTheme.mention_count)).limit(limit).all()

    @staticmethod
    def get_top_themes(db: Session, limit: int = 20) -> List[ReviewTheme]:
        return db.query(ReviewTheme).order_by(
            desc(ReviewTheme.mention_count)
        ).limit(limit).all()

    @staticmethod
    def update_or_create(
        db: Session,
        product_id: str,
        theme: str,
        aspect: str,
        sentiment: str,
        mention_count: int = 1
    ) -> ReviewTheme:
        """Update existing theme or create new one"""
        db_theme = db.query(ReviewTheme).filter(
            ReviewTheme.product_id == product_id,
            ReviewTheme.theme == theme,
            ReviewTheme.aspect == aspect
        ).first()

        if db_theme:
            db_theme.mention_count += mention_count
            db_theme.sentiment = sentiment
        else:
            db_theme = ReviewTheme(
                product_id=product_id,
                theme=theme,
                aspect=aspect,
                sentiment=sentiment,
                mention_count=mention_count
            )
            db.add(db_theme)

        db.commit()
        db.refresh(db_theme)
        return db_theme


class ReviewAnalyticsCRUD:
    @staticmethod
    def create(db: Session, analytics_data: ReviewAnalyticsCreate) -> ReviewAnalytics:
        db_analytics = ReviewAnalytics(**analytics_data.dict())
        db.add(db_analytics)
        db.commit()
        db.refresh(db_analytics)
        return db_analytics

    @staticmethod
    def get_latest_by_product(db: Session, product_id: str) -> Optional[ReviewAnalytics]:
        return db.query(ReviewAnalytics).filter(
            ReviewAnalytics.product_id == product_id
        ).order_by(desc(ReviewAnalytics.created_at)).first()

    @staticmethod
    def get_time_series(
        db: Session,
        product_id: str,
        period: str = "daily",
        days_back: int = 30
    ) -> List[ReviewAnalytics]:
        start_date = datetime.utcnow().date() - timedelta(days=days_back)
        return db.query(ReviewAnalytics).filter(
            ReviewAnalytics.product_id == product_id,
            ReviewAnalytics.period == period,
            ReviewAnalytics.period_date >= start_date
        ).order_by(ReviewAnalytics.period_date).all()


class UserPreferenceCRUD:
    @staticmethod
    def create(db: Session, pref_data: UserPreferenceCreate) -> UserPreference:
        db_pref = UserPreference(**pref_data.dict())
        db.add(db_pref)
        db.commit()
        db.refresh(db_pref)
        return db_pref

    @staticmethod
    def get_by_user(db: Session, user_id: str) -> Optional[UserPreference]:
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

    @staticmethod
    def update(
        db: Session,
        user_id: str,
        pref_update: UserPreferenceUpdate
    ) -> Optional[UserPreference]:
        db_pref = db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()

        if db_pref:
            for field, value in pref_update.dict(exclude_unset=True).items():
                if field == "preferences" and value:
                    # Merge with existing preferences
                    existing = db_pref.preferences or {}
                    existing.update(value)
                    db_pref.preferences = existing
                elif field == "viewed_products" and value:
                    # Add to viewed products (keep last 50)
                    existing = db_pref.viewed_products or []
                    for product_id in value:
                        if product_id not in existing:
                            existing.insert(0, product_id)
                    db_pref.viewed_products = existing[:50]
                else:
                    setattr(db_pref, field, value)

            db.commit()
            db.refresh(db_pref)

        return db_pref

    @staticmethod
    def add_viewed_product(db: Session, user_id: str, product_id: str):
        """Add product to user's viewed history"""
        db_pref = UserPreferenceCRUD.get_by_user(db, user_id)
        if db_pref:
            viewed = db_pref.viewed_products or []
            if product_id not in viewed:
                viewed.insert(0, product_id)
                db_pref.viewed_products = viewed[:50]  # Keep last 50
                db.commit()


class SearchHistoryCRUD:
    @staticmethod
    def create(db: Session, search_data: SearchHistoryCreate) -> SearchHistory:
        db_search = SearchHistory(**search_data.dict())
        db.add(db_search)
        db.commit()
        db.refresh(db_search)
        return db_search

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: str,
        limit: int = 20
    ) -> List[SearchHistory]:
        return db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).order_by(desc(SearchHistory.created_at)).limit(limit).all()

    @staticmethod
    def get_popular_searches(db: Session, limit: int = 10) -> List[Dict]:
        """Get most popular search queries"""
        result = db.query(
            SearchHistory.query,
            func.count(SearchHistory.id).label('count')
        ).filter(
            SearchHistory.query.isnot(None)
        ).group_by(SearchHistory.query).order_by(
            desc('count')
        ).limit(limit).all()

        return [{"query": q, "count": c} for q, c in result]


class UserRecommendationCRUD:
    @staticmethod
    def create(db: Session, rec_data: UserRecommendationCreate) -> UserRecommendation:
        db_rec = UserRecommendation(**rec_data.dict())
        db.add(db_rec)
        db.commit()
        db.refresh(db_rec)
        return db_rec

    @staticmethod
    def get_active_by_user(
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[UserRecommendation]:
        return db.query(UserRecommendation).filter(
            UserRecommendation.user_id == user_id,
            or_(
                UserRecommendation.expires_at.is_(None),
                UserRecommendation.expires_at > datetime.utcnow()
            )
        ).order_by(desc(UserRecommendation.score)).limit(limit).all()

    @staticmethod
    def mark_shown(db: Session, recommendation_id: str):
        """Mark recommendation as shown to user"""
        db_rec = db.query(UserRecommendation).filter(
            UserRecommendation.id == recommendation_id
        ).first()
        if db_rec:
            db_rec.shown_count += 1
            db.commit()

    @staticmethod
    def mark_clicked(db: Session, recommendation_id: str):
        """Mark recommendation as clicked by user"""
        db_rec = db.query(UserRecommendation).filter(
            UserRecommendation.id == recommendation_id
        ).first()
        if db_rec:
            db_rec.clicked += 1
            db.commit()

    @staticmethod
    def cleanup_expired(db: Session) -> int:
        """Remove expired recommendations"""
        count = db.query(UserRecommendation).filter(
            UserRecommendation.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return count


class DataSyncCRUD:
    @staticmethod
    def create(db: Session, sync_data: DataSyncCreate) -> DataSync:
        db_sync = DataSync(**sync_data.dict(), started_at=datetime.utcnow())
        db.add(db_sync)
        db.commit()
        db.refresh(db_sync)
        return db_sync

    @staticmethod
    def update(db: Session, sync_id: str, sync_update: DataSyncUpdate) -> Optional[DataSync]:
        db_sync = db.query(DataSync).filter(DataSync.id == sync_id).first()
        if db_sync:
            for field, value in sync_update.dict(exclude_unset=True).items():
                setattr(db_sync, field, value)
            db.commit()
            db.refresh(db_sync)
        return db_sync

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> List[DataSync]:
        return db.query(DataSync).order_by(
            desc(DataSync.created_at)
        ).limit(limit).all()

    @staticmethod
    def get_by_type(db: Session, sync_type: str, limit: int = 5) -> List[DataSync]:
        return db.query(DataSync).filter(
            DataSync.sync_type == sync_type
        ).order_by(desc(DataSync.created_at)).limit(limit).all()


class DataFreshnessCRUD:
    @staticmethod
    def create(db: Session, freshness_data: DataFreshnessCreate) -> DataFreshness:
        db_freshness = DataFreshness(**freshness_data.dict())
        db.add(db_freshness)
        db.commit()
        db.refresh(db_freshness)
        return db_freshness

    @staticmethod
    def update(
        db: Session,
        entity_type: str,
        freshness_update: DataFreshnessUpdate
    ) -> Optional[DataFreshness]:
        db_freshness = db.query(DataFreshness).filter(
            DataFreshness.entity_type == entity_type
        ).first()

        if db_freshness:
            for field, value in freshness_update.dict(exclude_unset=True).items():
                setattr(db_freshness, field, value)
            db.commit()
            db.refresh(db_freshness)

        return db_freshness

    @staticmethod
    def get_all(db: Session) -> List[DataFreshness]:
        return db.query(DataFreshness).all()

    @staticmethod
    def get_stale_entities(db: Session) -> List[DataFreshness]:
        return db.query(DataFreshness).filter(
            DataFreshness.is_stale == True
        ).all()

    @staticmethod
    def update_freshness(
        db: Session,
        entity_type: str,
        last_updated: datetime = None
    ) -> DataFreshness:
        """Update or create freshness record"""
        if last_updated is None:
            last_updated = datetime.utcnow()

        db_freshness = db.query(DataFreshness).filter(
            DataFreshness.entity_type == entity_type
        ).first()

        if db_freshness:
            db_freshness.last_updated = last_updated
            db_freshness.is_stale = False
        else:
            db_freshness = DataFreshness(
                entity_type=entity_type,
                last_updated=last_updated,
                is_stale=False
            )
            db.add(db_freshness)

        db.commit()
        db.refresh(db_freshness)
        return db_freshness

    @staticmethod
    def check_staleness(db: Session):
        """Check and update staleness for all entities"""
        entities = db.query(DataFreshness).all()

        for entity in entities:
            threshold_hours = entity.staleness_threshold_hours
            threshold_time = datetime.utcnow() - timedelta(hours=threshold_hours)

            entity.is_stale = entity.last_updated < threshold_time

        db.commit()


# Utility functions for batch operations

def bulk_create_themes(
    db: Session,
    product_id: str,
    themes_data: List[Dict[str, Any]]
) -> List[ReviewTheme]:
    """Bulk create review themes"""
    themes = []
    for theme_data in themes_data:
        theme = ReviewTheme(product_id=product_id, **theme_data)
        themes.append(theme)

    db.bulk_save_objects(themes)
    db.commit()
    return themes


def cleanup_old_data(db: Session, days_to_keep: int = 90):
    """Clean up old data"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    # Clean up old search history
    old_searches = db.query(SearchHistory).filter(
        SearchHistory.created_at < cutoff_date
    ).delete()

    # Clean up expired recommendations
    expired_recs = UserRecommendationCRUD.cleanup_expired(db)

    # Clean up old sync records
    old_syncs = db.query(DataSync).filter(
        DataSync.created_at < cutoff_date,
        DataSync.status.in_(["completed", "failed"])
    ).delete()

    db.commit()

    return {
        "old_searches_deleted": old_searches,
        "expired_recommendations": expired_recs,
        "old_syncs_deleted": old_syncs
    }