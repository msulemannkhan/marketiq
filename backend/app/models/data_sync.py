from sqlalchemy import Column, String, TIMESTAMP, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class DataSync(Base):
    __tablename__ = "data_sync"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_type = Column(String(50), nullable=False)  # prices, availability, reviews, specs
    source = Column(String(100))  # HP, Lenovo, Manual
    status = Column(String(50))  # pending, in_progress, completed, failed
    records_processed = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text)
    sync_metadata = Column(JSON)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<DataSync(id={self.id}, sync_type={self.sync_type}, status={self.status})>"


class DataFreshness(Base):
    __tablename__ = "data_freshness"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False, unique=True)  # products, reviews, prices, etc.
    last_updated = Column(TIMESTAMP, nullable=False)
    update_frequency = Column(String(50))  # hourly, daily, weekly
    next_update = Column(TIMESTAMP)
    is_stale = Column(Boolean, default=False)
    staleness_threshold_hours = Column(Integer, default=24)
    auto_sync_enabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DataFreshness(entity_type={self.entity_type}, is_stale={self.is_stale})>"