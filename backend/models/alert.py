"""Alert model."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, enum.Enum):
    STOCKOUT = "stockout"
    LOW_STOCK = "low_stock"
    PLANOGRAM_VIOLATION = "planogram_violation"
    SPOILAGE_RISK = "spoilage_risk"
    MISPLACED_ITEM = "misplaced_item"
    PRICE_TAG_MISSING = "price_tag_missing"
    UNUSUAL_DEPLETION = "unusual_depletion"


def _enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [e.value for e in enum_cls]


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    aisle_id = Column(Integer, ForeignKey("aisles.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    alert_type = Column(Enum(AlertType, values_callable=_enum_values, native_enum=False))
    severity = Column(Enum(AlertSeverity, values_callable=_enum_values, native_enum=False))
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    estimated_revenue_impact = Column(Float, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="alerts")
