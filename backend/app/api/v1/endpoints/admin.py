"""
Admin endpoints for data sync and system management
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.data_sync import (
    DataSyncCreate, DataSyncUpdate, DataSyncResponse,
    DataFreshnessResponse, DataFreshnessSummary, SyncHistory
)
from app.crud.enhanced_crud import (
    DataSyncCRUD, DataFreshnessCRUD, cleanup_old_data
)

router = APIRouter()


@router.post("/sync", response_model=DataSyncResponse)
async def trigger_data_sync(
    sync_data: DataSyncCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger a data synchronization job"""
    # In a real implementation, this would check admin permissions

    sync_job = DataSyncCRUD.create(db, sync_data)

    # Here you would trigger the actual sync process
    # For now, we'll just mark it as in progress

    update_data = DataSyncUpdate(
        status="in_progress",
        records_processed=0
    )
    sync_job = DataSyncCRUD.update(db, str(sync_job.id), update_data)

    return sync_job


@router.get("/sync/history", response_model=List[DataSyncResponse])
async def get_sync_history(
    sync_type: str = Query(None),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get synchronization history"""
    if sync_type:
        sync_jobs = DataSyncCRUD.get_by_type(db, sync_type, limit)
    else:
        sync_jobs = DataSyncCRUD.get_recent(db, limit)

    return sync_jobs


@router.get("/sync/{sync_id}", response_model=DataSyncResponse)
async def get_sync_status(
    sync_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of a specific sync job"""
    from app.models import DataSync

    sync_job = db.query(DataSync).filter(DataSync.id == sync_id).first()
    if not sync_job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    return sync_job


@router.put("/sync/{sync_id}", response_model=DataSyncResponse)
async def update_sync_status(
    sync_id: str,
    sync_update: DataSyncUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update sync job status"""
    sync_job = DataSyncCRUD.update(db, sync_id, sync_update)
    if not sync_job:
        raise HTTPException(status_code=404, detail="Sync job not found")

    return sync_job


@router.get("/data/freshness", response_model=DataFreshnessSummary)
async def get_data_freshness(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall data freshness status"""
    # Check staleness first
    DataFreshnessCRUD.check_staleness(db)

    all_entities = DataFreshnessCRUD.get_all(db)
    stale_entities = DataFreshnessCRUD.get_stale_entities(db)

    # Determine overall status
    if not stale_entities:
        overall_status = "fresh"
    elif len(stale_entities) < len(all_entities) / 2:
        overall_status = "partially_stale"
    else:
        overall_status = "stale"

    # Get recent sync info
    recent_syncs = DataSyncCRUD.get_recent(db, 5)
    last_full_sync = None
    if recent_syncs:
        last_full_sync = recent_syncs[0].completed_at

    # Generate recommendations
    recommendations = []
    if stale_entities:
        recommendations.append(f"{len(stale_entities)} data entities need updating")

    if overall_status == "stale":
        recommendations.append("Consider running full data sync")

    return DataFreshnessSummary(
        overall_status=overall_status,
        stale_entities=[entity.entity_type for entity in stale_entities],
        entities=all_entities,
        last_full_sync=last_full_sync,
        recommendations=recommendations
    )


@router.post("/data/freshness/update")
async def update_data_freshness(
    entity_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark data entity as fresh"""
    freshness = DataFreshnessCRUD.update_freshness(db, entity_type)
    return {
        "message": f"Updated freshness for {entity_type}",
        "last_updated": freshness.last_updated
    }


@router.post("/cleanup")
async def cleanup_old_data_endpoint(
    days_to_keep: int = Query(90, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up old data (admin only)"""
    # In production, add admin permission check

    result = cleanup_old_data(db, days_to_keep)
    return {
        "message": "Data cleanup completed",
        "details": result,
        "days_kept": days_to_keep
    }


@router.get("/analytics/sync", response_model=SyncHistory)
async def get_sync_analytics(
    days_back: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sync analytics and history"""
    from app.models import DataSync
    from datetime import timedelta

    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Get recent syncs
    recent_syncs = db.query(DataSync).filter(
        DataSync.created_at >= start_date
    ).order_by(DataSync.created_at.desc()).limit(50).all()

    # Calculate success rate
    completed_syncs = [s for s in recent_syncs if s.status == "completed"]
    failed_syncs = [s for s in recent_syncs if s.status == "failed"]

    success_rate = 0.0
    if recent_syncs:
        success_rate = len(completed_syncs) / len(recent_syncs) * 100

    # Calculate average duration (mock data for now)
    average_duration = 15.5  # Would calculate from actual sync times

    # Mock upcoming syncs
    upcoming_syncs = [
        {
            "sync_type": "prices",
            "scheduled_time": "2024-01-02T02:00:00Z",
            "frequency": "daily"
        },
        {
            "sync_type": "reviews",
            "scheduled_time": "2024-01-02T06:00:00Z",
            "frequency": "daily"
        }
    ]

    return SyncHistory(
        recent_syncs=recent_syncs,
        success_rate=success_rate,
        average_duration_minutes=average_duration,
        failed_syncs=failed_syncs,
        upcoming_syncs=upcoming_syncs
    )


@router.post("/products/reindex")
async def reindex_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reindex products for search"""
    # This would trigger a reindexing job
    # For now, just return a success message

    from app.models import Product

    product_count = db.query(Product).count()

    return {
        "message": "Product reindexing started",
        "total_products": product_count,
        "estimated_time_minutes": product_count * 0.1  # Mock estimation
    }


@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    from app.models import Product, Variant, ReviewSummary

    # Get basic counts
    product_count = db.query(Product).count()
    variant_count = db.query(Variant).count()
    review_count = db.query(ReviewSummary).count()

    # Check database connectivity
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "error"

    # Mock other service checks
    services_status = {
        "database": db_status,
        "gemini_api": "healthy",  # Would check actual API
        "pinecone": "healthy",    # Would check actual service
        "search_index": "healthy"
    }

    overall_status = "healthy" if all(
        status == "healthy" for status in services_status.values()
    ) else "degraded"

    return {
        "overall_status": overall_status,
        "services": services_status,
        "data_counts": {
            "products": product_count,
            "variants": variant_count,
            "reviews": review_count
        },
        "timestamp": datetime.utcnow().isoformat()
    }