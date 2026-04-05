"""Aggregations over seeded DB for API responses."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.alert import Alert, AlertSeverity, AlertType
from models.product import Product, ProductCategory
from models.scan import ShelfScan
from models.store import Aisle, ShelfState, Store


def store_occupancy_avg(db: Session, store_id: int) -> float:
    row = (
        db.query(func.avg(Aisle.occupancy_pct))
        .filter(Aisle.store_id == store_id)
        .scalar()
    )
    return float(row) if row is not None else 0.0


def count_unresolved_alerts(db: Session, store_id: int | None = None) -> int:
    q = db.query(Alert).filter(Alert.is_resolved.is_(False))
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    return q.count()


def sum_revenue_at_risk(db: Session, store_id: int | None = None) -> float:
    q = db.query(func.coalesce(func.sum(Alert.estimated_revenue_impact), 0.0)).filter(
        Alert.is_resolved.is_(False)
    )
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    row = q.scalar()
    return float(row or 0.0)


def count_alert_type(
    db: Session, alert_type: AlertType, store_id: int | None = None, unresolved_only: bool = True
) -> int:
    q = db.query(Alert).filter(Alert.alert_type == alert_type)
    if unresolved_only:
        q = q.filter(Alert.is_resolved.is_(False))
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    return q.count()


def waste_risk_count(db: Session, store_id: int | None = None) -> int:
    """Perishable products with spoilage alerts or heuristic count."""
    q = (
        db.query(Alert)
        .filter(Alert.alert_type == AlertType.SPOILAGE_RISK)
        .filter(Alert.is_resolved.is_(False))
    )
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    n = q.count()
    if n == 0:
        perishable = db.query(Product).filter(Product.is_perishable.is_(True)).count()
        return min(perishable, 12) if store_id is None else min(3, perishable)
    return n


def scan_coverage_pct(db: Session, store_id: int) -> float:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store or not store.total_aisles:
        return 0.0
    since = datetime.utcnow() - timedelta(hours=24)
    n_scans = (
        db.query(ShelfScan)
        .filter(ShelfScan.store_id == store_id, ShelfScan.timestamp >= since)
        .count()
    )
    return min(100.0, (n_scans / max(store.total_aisles, 1)) * 100.0)


def predicted_stockouts_24h(db: Session, store_id: int | None = None) -> int:
    q = db.query(Alert).filter(
        Alert.is_resolved.is_(False),
        Alert.alert_type.in_([AlertType.STOCKOUT, AlertType.LOW_STOCK]),
    )
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    return q.count()


def shelf_states_for_aisle(db: Session, aisle_id: int, limit: int = 500) -> list[ShelfState]:
    return (
        db.query(ShelfState)
        .filter(ShelfState.aisle_id == aisle_id)
        .order_by(ShelfState.timestamp.desc())
        .limit(limit)
        .all()
    )


def trends_series(
    db: Session,
    store_id: int | None,
    days: int,
    category: str | None,
) -> list[dict[str, Any]]:
    since = datetime.utcnow() - timedelta(days=days)
    q = (
        db.query(
            func.date(ShelfState.timestamp).label("d"),
            func.avg(ShelfState.occupancy_pct).label("avg_occ"),
        )
        .join(Aisle, ShelfState.aisle_id == Aisle.id)
        .filter(ShelfState.timestamp >= since)
    )
    if store_id is not None:
        q = q.filter(Aisle.store_id == store_id)
    if category:
        q = q.filter(Aisle.category == category)
    rows = q.group_by(func.date(ShelfState.timestamp)).order_by(func.date(ShelfState.timestamp)).all()
    return [{"date": str(r.d), "avg_occupancy_pct": round(float(r.avg_occ or 0), 2)} for r in rows]


def alert_summary_counts(db: Session, store_id: int | None = None) -> dict[str, int]:
    q = db.query(Alert.severity, func.count(Alert.id)).filter(Alert.is_resolved.is_(False))
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    rows = q.group_by(Alert.severity).all()
    out = {s.value: 0 for s in AlertSeverity}
    for sev, cnt in rows:
        key = sev.value if hasattr(sev, "value") else str(sev)
        out[key] = cnt
    return out
