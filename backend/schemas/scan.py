from datetime import datetime

from pydantic import BaseModel, Field


class ShelfScanRequest(BaseModel):
    store_id: int
    aisle_id: int | None = None
    scan_type: str = "manual_upload"


class DetectedProduct(BaseModel):
    product_name: str
    sku: str | None = None
    bounding_box: dict
    confidence: float
    quantity_estimated: int
    shelf_position: int


class ShelfAnalysisResponse(BaseModel):
    scan_id: int
    timestamp: datetime
    overall_occupancy: float
    products_detected: int
    empty_slots: int
    detections: list[DetectedProduct]
    issues: list[dict]
    gemini_insight: str
    processing_time_ms: int
    confidence_avg: float


class ScanHistoryItem(BaseModel):
    scan_id: int
    store_id: int
    aisle_id: int | None
    timestamp: datetime
    scan_type: str | None
    overall_occupancy: float | None
    products_detected: int | None
    processing_time_ms: int | None


class BatchScanResponse(BaseModel):
    results: list[ShelfAnalysisResponse]
    total: int
