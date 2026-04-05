from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.alert import Alert
from models.product import Product
from models.store import Store
from schemas.analytics import (
    ComparisonsResponse,
    DashboardGlobal,
    DepletionForecast,
    StoreBenchmark,
    TrendsResponse,
    WasteRiskItem,
)
from services.mock_scan import mock_depletion_forecasts
from services.query_stats import (
    count_alert_type,
    count_unresolved_alerts,
    predicted_stockouts_24h,
    store_occupancy_avg,
    sum_revenue_at_risk,
    waste_risk_count,
)
from models.alert import AlertType

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardGlobal)
def dashboard(db: Session = Depends(get_db)) -> DashboardGlobal:
    stores = db.query(Store).all()
    n = len(stores)
    avg_health = sum(s.health_score or 0 for s in stores) / max(n, 1)
    occs = [store_occupancy_avg(db, s.id) for s in stores]
    avg_occ = sum(occs) / max(len(occs), 1)
    return DashboardGlobal(
        store_count=n,
        avg_health_score=round(avg_health, 1),
        occupancy_avg=round(avg_occ, 2),
        active_alerts=count_unresolved_alerts(db),
        total_stockouts=count_alert_type(db, AlertType.STOCKOUT),
        predicted_stockouts_24h=predicted_stockouts_24h(db),
        waste_risk_items=waste_risk_count(db),
        revenue_at_risk_eur=round(sum_revenue_at_risk(db), 2),
    )


@router.get("/depletion", response_model=list[DepletionForecast])
def depletion(
    store_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[DepletionForecast]:
    raw = mock_depletion_forecasts(db, store_id)
    return [
        DepletionForecast(
            product_id=r["product_id"],
            product_name=r["product_name"],
            current_quantity=r["current_quantity"],
            depletion_rate_per_hour=r["depletion_rate_per_hour"],
            predicted_stockout_time=r["predicted_stockout_time"],
            recommended_restock_quantity=r["recommended_restock_quantity"],
            confidence=r["confidence"],
        )
        for r in raw
    ]


@router.get("/trends", response_model=TrendsResponse)
def trends(
    store_id: int | None = None,
    days: int = 7,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> TrendsResponse:
    from services.query_stats import trends_series

    series = trends_series(db, store_id, days, category)
    return TrendsResponse(store_id=store_id, days=days, category=category, series=series)


@router.get("/waste-risk", response_model=list[WasteRiskItem])
def waste_risk(store_id: int | None = None, db: Session = Depends(get_db)) -> list[WasteRiskItem]:
    spoilage = (
        db.query(Alert, Product)
        .outerjoin(Product, Alert.product_id == Product.id)
        .filter(Alert.alert_type == AlertType.SPOILAGE_RISK, Alert.is_resolved.is_(False))
    )
    if store_id is not None:
        spoilage = spoilage.filter(Alert.store_id == store_id)
    rows = spoilage.limit(50).all()
    out: list[WasteRiskItem] = []
    for alert, prod in rows:
        name = prod.name if prod else (alert.title or "Product")
        pid = prod.id if prod else 0
        cat = prod.category.value if prod and prod.category else None
        sl = prod.shelf_life_days if prod else 5
        out.append(
            WasteRiskItem(
                product_id=pid,
                product_name=name,
                category=cat,
                shelf_life_days=sl,
                days_to_expiry_estimate=2,
                risk_score=0.72,
                recommended_action=alert.recommended_action or "Rotate stock; mark down near expiry.",
            )
        )
    if not out:
        for p in db.query(Product).filter(Product.is_perishable.is_(True)).limit(15).all():
            out.append(
                WasteRiskItem(
                    product_id=p.id,
                    product_name=p.name,
                    category=p.category.value if p.category else None,
                    shelf_life_days=p.shelf_life_days,
                    days_to_expiry_estimate=3,
                    risk_score=0.55,
                    recommended_action="Monitor cold chain and facing depth.",
                )
            )
    return out


@router.get("/comparisons", response_model=ComparisonsResponse)
def comparisons(db: Session = Depends(get_db)) -> ComparisonsResponse:
    stores = db.query(Store).order_by(Store.id).all()
    benchmarks: list[StoreBenchmark] = []
    for s in stores:
        benchmarks.append(
            StoreBenchmark(
                store_id=s.id,
                store_name=s.name,
                chain=s.chain,
                health_score=s.health_score,
                occupancy_avg=round(store_occupancy_avg(db, s.id), 2),
                active_alerts=count_unresolved_alerts(db, s.id),
                revenue_at_risk_eur=round(sum_revenue_at_risk(db, s.id), 2),
            )
        )
    return ComparisonsResponse(stores=benchmarks)
