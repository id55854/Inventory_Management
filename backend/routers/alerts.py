from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.alert import Alert, AlertSeverity
from models.product import Product
from schemas.alert import AlertOut, AlertSummaryOut, RestockRecommendation
from services.query_stats import alert_summary_counts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    store_id: int | None = None,
    severity: str | None = None,
    resolved: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Alert]:
    q = db.query(Alert)
    if store_id is not None:
        q = q.filter(Alert.store_id == store_id)
    if severity is not None:
        try:
            sev = AlertSeverity(severity)
            q = q.filter(Alert.severity == sev)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid severity") from None
    if resolved is not None:
        q = q.filter(Alert.is_resolved == resolved)
    return q.order_by(Alert.created_at.desc()).limit(500).all()


@router.get("/summary", response_model=AlertSummaryOut)
def alerts_summary(
    store_id: int | None = None,
    db: Session = Depends(get_db),
) -> AlertSummaryOut:
    by_sev = alert_summary_counts(db, store_id)
    total = sum(by_sev.values())
    return AlertSummaryOut(by_severity=by_sev, total_unresolved=total)


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)) -> dict:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    return {"id": alert.id, "is_resolved": True}


@router.get("/{alert_id}/recommendation", response_model=RestockRecommendation)
def alert_recommendation(alert_id: int, db: Session = Depends(get_db)) -> RestockRecommendation:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    prod = (
        db.query(Product).filter(Product.id == alert.product_id).first()
        if alert.product_id
        else None
    )
    qty = (prod.max_shelf_quantity or 20) // 2 if prod else 12
    urgency = alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity)
    return RestockRecommendation(
        alert_id=alert.id,
        product_id=alert.product_id,
        product_name=prod.name if prod else None,
        recommended_quantity=qty,
        rationale=alert.recommended_action
        or "Restock to planogram target and verify facing depth.",
        urgency=urgency,
        estimated_revenue_if_unaddressed_eur=alert.estimated_revenue_impact,
    )
