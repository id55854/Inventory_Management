"""Store, Aisle, ShelfState SQLAlchemy models."""

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from database import Base


class StoreStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


def _enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [e.value for e in enum_cls]


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(
        Enum(StoreStatus, values_callable=_enum_values, native_enum=False),
        default=StoreStatus.ACTIVE,
    )
    total_aisles = Column(Integer, nullable=True)
    total_shelves = Column(Integer, nullable=True)
    health_score = Column(Float, default=100.0)
    last_scan_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    aisles = relationship("Aisle", back_populates="store")
    scans = relationship("ShelfScan", back_populates="store")
    alerts = relationship("Alert", back_populates="store")


class Aisle(Base):
    __tablename__ = "aisles"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    name = Column(String, nullable=True)
    aisle_number = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    total_shelves = Column(Integer, default=5)
    occupancy_pct = Column(Float, default=100.0)
    compliance_score = Column(Float, default=100.0)
    last_scan_at = Column(DateTime, nullable=True)

    store = relationship("Store", back_populates="aisles")
    shelf_states = relationship("ShelfState", back_populates="aisle")
    scans = relationship("ShelfScan", back_populates="aisle")


class ShelfState(Base):
    """Point-in-time snapshot of shelf state — the core time-series table."""

    __tablename__ = "shelf_states"

    id = Column(Integer, primary_key=True)
    aisle_id = Column(Integer, ForeignKey("aisles.id"))
    shelf_position = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    occupancy_pct = Column(Float, nullable=True)
    product_counts = Column(JSON, nullable=True)
    detected_issues = Column(JSON, nullable=True)
    scan_id = Column(Integer, ForeignKey("shelf_scans.id"), nullable=True)

    aisle = relationship("Aisle", back_populates="shelf_states")
    scan = relationship("ShelfScan", back_populates="shelf_states")
