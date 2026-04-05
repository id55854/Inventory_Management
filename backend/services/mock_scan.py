"""Derive plausible scan analysis from seeded product catalog."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from models.product import Product
from schemas.scan import DetectedProduct, ShelfAnalysisResponse


def build_mock_analysis(
    db: Session,
    scan_id: int,
    timestamp: datetime,
    overall_occupancy: float,
    processing_time_ms: int,
) -> ShelfAnalysisResponse:
    products = db.query(Product).order_by(Product.id).limit(8).all()
    detections: list[DetectedProduct] = []
    for i, p in enumerate(products):
        x = 0.05 + (i % 4) * 0.22
        y = 0.1 + (i // 4) * 0.35
        detections.append(
            DetectedProduct(
                product_name=p.name,
                sku=p.sku,
                bounding_box={"x": x, "y": y, "w": 0.18, "h": 0.25},
                confidence=round(random.uniform(0.55, 0.95), 3),
                quantity_estimated=random.randint(1, 4),
                shelf_position=(i % 5) + 1,
            )
        )

    empty_slots = random.randint(0, 3)
    issues = [
        {
            "type": "low_stock",
            "product": products[0].name if products else "unknown",
            "severity": "medium",
        }
    ]
    conf_avg = sum(d.confidence for d in detections) / max(len(detections), 1)

    return ShelfAnalysisResponse(
        scan_id=scan_id,
        timestamp=timestamp,
        overall_occupancy=overall_occupancy,
        products_detected=len(detections),
        empty_slots=empty_slots,
        detections=detections,
        issues=issues,
        gemini_insight=(
            "Mock analysis: shelf shows typical weekday depletion. "
            "Prioritize restocking high-velocity dairy and snacks."
        ),
        processing_time_ms=processing_time_ms,
        confidence_avg=round(conf_avg, 3),
    )


def mock_depletion_forecasts(db: Session, store_id: int | None, limit: int = 50):
    """Build depletion rows from product velocity (seeded)."""
    q = db.query(Product).order_by(Product.id)
    rows = q.limit(limit).all()
    out = []
    now = datetime.utcnow()
    for p in rows:
        rate = max(0.1, (p.avg_daily_sales or 10) / 24.0)
        qty = random.randint(1, min(p.max_shelf_quantity or 20, 15))
        hours_left = qty / rate if rate > 0 else 99.0
        out.append(
            {
                "product_id": p.id,
                "product_name": p.name,
                "current_quantity": qty,
                "depletion_rate_per_hour": round(rate, 3),
                "predicted_stockout_time": now + timedelta(hours=hours_left),
                "recommended_restock_quantity": min(
                    p.max_shelf_quantity or 20, max(0, (p.max_shelf_quantity or 20) - qty)
                ),
                "confidence": round(random.uniform(0.7, 0.95), 2),
            }
        )
    out.sort(key=lambda x: x["predicted_stockout_time"])
    return out
