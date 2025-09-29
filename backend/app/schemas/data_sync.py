from pydantic import BaseModel, UUID4, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DataSyncBase(BaseModel):
    sync_type: str = Field(..., max_length=50)  # prices, availability, reviews, specs
    source: Optional[str] = Field(None, max_length=100)  # HP, Lenovo, Manual
    status: Optional[str] = Field(default="pending", max_length=50)


class DataSyncCreate(DataSyncBase):
    sync_metadata: Optional[Dict[str, Any]] = None


class DataSyncUpdate(BaseModel):
    status: Optional[str] = None
    records_processed: Optional[int] = None
    records_updated: Optional[int] = None
    records_failed: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class DataSyncResponse(DataSyncBase):
    id: UUID4
    records_processed: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    sync_metadata: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DataFreshnessBase(BaseModel):
    entity_type: str = Field(..., max_length=50)  # products, reviews, prices, etc.
    update_frequency: Optional[str] = Field(None, max_length=50)  # hourly, daily, weekly
    staleness_threshold_hours: int = Field(default=24, ge=1)
    auto_sync_enabled: bool = False


class DataFreshnessCreate(DataFreshnessBase):
    last_updated: datetime


class DataFreshnessUpdate(BaseModel):
    last_updated: Optional[datetime] = None
    next_update: Optional[datetime] = None
    is_stale: Optional[bool] = None
    update_frequency: Optional[str] = None
    staleness_threshold_hours: Optional[int] = None
    auto_sync_enabled: Optional[bool] = None


class DataFreshnessResponse(DataFreshnessBase):
    id: UUID4
    last_updated: datetime
    next_update: Optional[datetime] = None
    is_stale: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataFreshnessSummary(BaseModel):
    overall_status: str = "fresh"  # fresh, partially_stale, stale
    stale_entities: List[str] = []
    entities: List[DataFreshnessResponse] = []
    last_full_sync: Optional[datetime] = None
    next_scheduled_sync: Optional[datetime] = None
    recommendations: List[str] = []

    class Config:
        from_attributes = True


class SyncHistory(BaseModel):
    recent_syncs: List[DataSyncResponse] = []
    success_rate: float = 0.0
    average_duration_minutes: float = 0.0
    failed_syncs: List[DataSyncResponse] = []
    upcoming_syncs: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True