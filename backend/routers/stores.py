from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.alert import AlertType
from models.store import Aisle, ShelfState, Store
from schemas.analytics import StoreKPIs
from schemas.store import (
    AisleBrief,
    AisleDetail,
    HeatmapCell,
    HeatmapResponse,
    ShelfStateBrief,
    StoreDetail,
    StoreSummary,
)
from services.query_stats import (
    count_alert_type,
    count_unresolved_alerts,
    predicted_stockouts_24h,
    scan_coverage_pct,
    store_occupancy_avg,
    sum_revenue_at_risk,
    waste_risk_count,
)
router = APIRouter(prefix="/stores", tags=["stores"])


def _status_str(store: Store) -> str:
    s = store.status
    return s.value if hasattr(s, "value") else str(s)


@router.get("", response_model=list[StoreSummary])
def list_stores(db: Session = Depends(get_db)) -> list[StoreSummary]:
    stores = db.query(Store).order_by(Store.id).all()
    out: list[StoreSummary] = []
    for s in stores:
        occ = store_occupancy_avg(db, s.id)
        n_alerts = count_unresolved_alerts(db, s.id)
        out.append(
            StoreSummary(
                id=s.id,
                name=s.name,
                chain=s.chain,
                city=s.city,
                health_score=s.health_score,
                status=_status_str(s),
                last_scan_at=s.last_scan_at,
                occupancy_avg=round(occ, 2),
                active_alerts=n_alerts,
            )
        )
    return out


@router.get("/{store_id}", response_model=StoreDetail)
def get_store(store_id: int, db: Session = Depends(get_db)) -> StoreDetail:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    occ = store_occupancy_avg(db, store_id)
    return StoreDetail(
        id=store.id,
        name=store.name,
        chain=store.chain,
        city=store.city,
        address=store.address,
        latitude=store.latitude,
        longitude=store.longitude,
        status=_status_str(store),
        health_score=store.health_score,
        total_aisles=store.total_aisles,
        total_shelves=store.total_shelves,
        last_scan_at=store.last_scan_at,
        created_at=store.created_at,
        occupancy_avg=round(occ, 2),
    )


@router.get("/{store_id}/kpis", response_model=StoreKPIs)
def get_store_kpis(store_id: int, db: Session = Depends(get_db)) -> StoreKPIs:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    occ = store_occupancy_avg(db, store_id)
    return StoreKPIs(
        store_id=store.id,
        store_name=store.name,
        health_score=float(store.health_score or 0.0),
        occupancy_avg=round(occ, 2),
        stockout_count=count_alert_type(db, AlertType.STOCKOUT, store_id),
        active_alerts=count_unresolved_alerts(db, store_id),
        predicted_stockouts_24h=predicted_stockouts_24h(db, store_id),
        waste_risk_items=waste_risk_count(db, store_id),
        revenue_at_risk_eur=round(sum_revenue_at_risk(db, store_id), 2),
        scan_coverage_pct=round(scan_coverage_pct(db, store_id), 1),
    )


@router.get("/{store_id}/aisles", response_model=list[AisleBrief])
def list_aisles(store_id: int, db: Session = Depends(get_db)) -> list[Aisle]:
    if not db.query(Store).filter(Store.id == store_id).first():
        raise HTTPException(status_code=404, detail="Store not found")
    return (
        db.query(Aisle).filter(Aisle.store_id == store_id).order_by(Aisle.aisle_number).all()
    )


@router.get("/{store_id}/aisles/{aisle_id}", response_model=AisleDetail)
def get_aisle(
    store_id: int, aisle_id: int, db: Session = Depends(get_db)
) -> AisleDetail:
    aisle = (
        db.query(Aisle)
        .filter(Aisle.id == aisle_id, Aisle.store_id == store_id)
        .first()
    )
    if not aisle:
        raise HTTPException(status_code=404, detail="Aisle not found")
    states = (
        db.query(ShelfState)
        .filter(ShelfState.aisle_id == aisle_id)
        .order_by(ShelfState.timestamp.desc())
        .limit(200)
        .all()
    )
    return AisleDetail(
        aisle=AisleBrief.model_validate(aisle),
        shelf_states=[ShelfStateBrief.model_validate(s) for s in states],
    )


@router.get("/{store_id}/heatmap", response_model=HeatmapResponse)
def get_heatmap(store_id: int, db: Session = Depends(get_db)) -> HeatmapResponse:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    aisles = (
        db.query(Aisle).filter(Aisle.store_id == store_id).order_by(Aisle.aisle_number).all()
    )
    grid: list[HeatmapCell] = []
    for aisle in aisles:
        for row in range(1, 6):
            ss = (
                db.query(ShelfState)
                .filter(ShelfState.aisle_id == aisle.id, ShelfState.shelf_position == row)
                .order_by(ShelfState.timestamp.desc())
                .first()
            )
            occ = float(ss.occupancy_pct) if ss and ss.occupancy_pct is not None else float(
                aisle.occupancy_pct or 0.0
            )
            grid.append(
                HeatmapCell(
                    aisle_id=aisle.id,
                    aisle_number=aisle.aisle_number,
                    category=aisle.category,
                    shelf_row=row,
                    occupancy_pct=round(occ, 1),
                )
            )
    return HeatmapResponse(
        store_id=store.id,
        store_name=store.name,
        grid=grid,
        aisles=[AisleBrief.model_validate(a) for a in aisles],
    )
