import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.scan import ShelfScan
from models.store import Store
from schemas.insights import (
    AnalyzeShelfRequest,
    AnalyzeShelfResponse,
    DailyBriefResponse,
    StoreReportRequest,
    StoreReportResponse,
)
from services.gemini import decode_base64_image, get_engine
from services.query_stats import count_unresolved_alerts, sum_revenue_at_risk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


def _fallback_analyze_shelf() -> AnalyzeShelfResponse:
    return AnalyzeShelfResponse(
        summary=(
            "Gemini is not configured (set GEMINI_API_KEY). "
            "Mock: shelves show mixed fill levels — focus on dairy facing and snack gaps."
        ),
        issues=[
            {"type": "gap", "severity": "medium", "region": "center"},
            {"type": "price_tag", "severity": "low", "region": "left"},
        ],
        recommendations=[
            "Restock fast movers on eye level first.",
            "Verify planogram for aisle ends.",
        ],
    )


@router.post("/analyze-shelf", response_model=AnalyzeShelfResponse)
async def analyze_shelf(body: AnalyzeShelfRequest) -> AnalyzeShelfResponse:
    if not body.image_base64 or not body.image_base64.strip():
        raise HTTPException(status_code=400, detail="image_base64 is required")

    engine = get_engine()
    if not engine:
        return _fallback_analyze_shelf()

    try:
        raw = decode_base64_image(body.image_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {e}") from e

    try:
        data = await engine.analyze_shelf_insight_json(raw, body.context)
    except Exception as e:  # pragma: no cover
        logger.warning("Gemini analyze-shelf failed: %s", e)
        return _fallback_analyze_shelf()

    summary = str(data.get("summary") or data.get("raw_response") or "Analysis unavailable.")
    issues_raw = data.get("issues") or []
    recs = data.get("recommendations") or []
    if not isinstance(recs, list):
        recs = []
    recs = [str(x) for x in recs if x]

    issues: list[dict] = []
    for it in issues_raw if isinstance(issues_raw, list) else []:
        if isinstance(it, dict):
            issues.append(
                {
                    "type": str(it.get("type", "issue")),
                    "severity": str(it.get("severity", "medium")),
                    "region": str(it.get("region", "")),
                }
            )

    if not summary.strip():
        return _fallback_analyze_shelf()

    return AnalyzeShelfResponse(summary=summary, issues=issues, recommendations=recs)


@router.post("/store-report", response_model=StoreReportResponse)
async def store_report(body: StoreReportRequest, db: Session = Depends(get_db)) -> StoreReportResponse:
    store = db.query(Store).filter(Store.id == body.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    alerts_n = count_unresolved_alerts(db, store.id)
    rev = sum_revenue_at_risk(db, store.id)

    engine = get_engine()
    if engine:
        store_data = {
            "name": store.name,
            "chain": store.chain,
            "city": store.city,
            "health_score": store.health_score,
            "total_aisles": store.total_aisles,
            "active_alerts": alerts_n,
            "revenue_at_risk_eur": rev,
        }
        try:
            data = await engine.generate_store_report(store_data)
        except Exception as e:  # pragma: no cover
            logger.warning("Gemini store-report failed: %s", e)
            data = {}
        summary = data.get("executive_summary") or data.get("raw_response")
        if isinstance(summary, str) and summary.strip():
            report = summary.strip()
        else:
            report = (
                f"{store.name} ({store.chain}) — health score {store.health_score or 0:.0f}/100. "
                f"Active alerts: {alerts_n}. Revenue at risk: €{rev:.2f}."
            )
        actions = data.get("critical_actions") or data.get("recommendations") or []
        if isinstance(actions, str):
            actions = [actions]
        elif not isinstance(actions, list):
            actions = []
        key_actions = [str(a) for a in actions if a][:12]
        if not key_actions:
            key_actions = [
                "Clear critical stockouts in snack and dairy zones.",
                "Rotate produce with nearest expiry to front.",
                "Validate shelf labels on promo SKUs.",
            ]
        return StoreReportResponse(report=report, key_actions=key_actions)

    report = (
        f"{store.name} ({store.chain}) — health score {store.health_score or 0:.0f}/100. "
        f"Active operational alerts: {alerts_n}. Estimated revenue at risk: €{rev:.2f}. "
        "Prioritize restocks on perishable categories before evening peak."
    )
    actions = [
        "Clear critical stockouts in snack and dairy zones.",
        "Rotate produce with nearest expiry to front.",
        "Validate shelf labels on promo SKUs.",
    ]
    return StoreReportResponse(report=report, key_actions=actions)


@router.get("/daily-brief", response_model=DailyBriefResponse)
async def daily_brief(store_id: int, db: Session = Depends(get_db)) -> DailyBriefResponse:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    n = count_unresolved_alerts(db, store_id)
    scans = (
        db.query(ShelfScan)
        .filter(ShelfScan.store_id == store_id)
        .order_by(ShelfScan.timestamp.desc())
        .limit(30)
        .all()
    )
    scan_history = [
        {
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "occupancy": s.overall_occupancy,
            "products_detected": s.products_detected,
            "scan_type": s.scan_type,
        }
        for s in scans
    ]

    engine = get_engine()
    if engine:
        try:
            brief = await engine.daily_brief(store_id, scan_history)
        except Exception as e:  # pragma: no cover
            logger.warning("Gemini daily-brief failed: %s", e)
            brief = ""
        if not brief.strip():
            brief = (
                f"Morning brief for {store.name}: {n} open alerts. "
                f"Health score {store.health_score or 0:.0f} — maintain facing discipline."
            )
    else:
        brief = (
            f"Morning brief for {store.name}: {n} open alerts. "
            f"Focus on high-traffic categories and confirm cold chain before 10:00. "
            f"Health score {store.health_score or 0:.0f} — maintain facing discipline."
        )

    return DailyBriefResponse(
        store_id=store_id,
        brief=brief,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )
