"""ShelfScan model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from database import Base


class ShelfScan(Base):
    __tablename__ = "shelf_scans"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    aisle_id = Column(Integer, ForeignKey("aisles.id"), nullable=True)
    image_path = Column(String, nullable=True)
    scan_type = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(Integer, nullable=True)
    products_detected = Column(Integer, nullable=True)
    empty_slots_detected = Column(Integer, nullable=True)
    overall_occupancy = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    raw_detections = Column(JSON, nullable=True)
    gemini_summary = Column(String, nullable=True)

    store = relationship("Store", back_populates="scans")
    aisle = relationship("Aisle", back_populates="scans")
    shelf_states = relationship("ShelfState", back_populates="scan")
