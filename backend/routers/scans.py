import logging
import time
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from models.scan import ShelfScan
from schemas.scan import BatchScanResponse, ScanHistoryItem, ShelfAnalysisResponse
from services.gemini import get_engine
from services.mock_scan import build_mock_analysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])

_UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "uploads"
_MAX_BYTES = 10 * 1024 * 1024


def _ensure_upload_dir() -> None:
    _UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


async def _enrich_with_gemini(
    image_bytes: bytes,
    analysis: ShelfAnalysisResponse,
    scan: ShelfScan,
    store_id: int,
    aisle_id: int | None,
    db: Session,
) -> ShelfAnalysisResponse:
    """Section 6.2 — replace mock Gemini text with API when configured."""
    engine = get_engine()
    if not engine:
        return analysis
    try:
        detections = [d.model_dump() for d in analysis.detections]
        issues = analysis.issues or []
        ctx = (
            f"Store {store_id}, Aisle {aisle_id}"
            if aisle_id is not None
            else f"Store {store_id}"
        )
        insight = await engine.analyze_shelf(
            image_bytes,
            detections,
            analysis.overall_occupancy,
            issues,
            ctx,
        )
        out = analysis.model_copy(update={"gemini_insight": insight})
        scan.gemini_summary = insight
        db.commit()
        return out
    except Exception as e:  # pragma: no cover
        logger.warning("Gemini shelf analysis failed: %s", e)
        return analysis


@router.post("/upload", response_model=ShelfAnalysisResponse)
async def upload_shelf_scan(
    image: UploadFile = File(...),
    store_id: int = Form(...),
    aisle_id: int | None = Form(None),
    db: Session = Depends(get_db),
) -> ShelfAnalysisResponse:
    _ensure_upload_dir()
    start = time.time()
    contents = await image.read()
    if len(contents) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    name = f"{uuid.uuid4().hex}_{image.filename or 'shelf.jpg'}"
    path = _UPLOAD_ROOT / name
    path.write_bytes(contents)

    overall = round(min(100.0, max(5.0, len(contents) / 50000)), 1)
    proc_ms = int((time.time() - start) * 1000) + 5

    scan = ShelfScan(
        store_id=store_id,
        aisle_id=aisle_id,
        image_path=str(path),
        scan_type="manual_upload",
        timestamp=datetime.utcnow(),
        processing_time_ms=proc_ms,
        products_detected=0,
        empty_slots_detected=0,
        overall_occupancy=overall,
        confidence_score=0.8,
        raw_detections=None,
        gemini_summary=None,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    analysis = build_mock_analysis(db, scan.id, scan.timestamp, overall, proc_ms)
    scan.products_detected = analysis.products_detected
    scan.empty_slots_detected = analysis.empty_slots
    scan.confidence_score = analysis.confidence_avg
    scan.gemini_summary = analysis.gemini_insight
    db.commit()

    analysis = await _enrich_with_gemini(contents, analysis, scan, store_id, aisle_id, db)
    return analysis


@router.post("/batch", response_model=BatchScanResponse)
async def batch_upload(
    store_id: int = Form(...),
    aisle_id: int | None = Form(None),
    images: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> BatchScanResponse:
    _ensure_upload_dir()
    results: list[ShelfAnalysisResponse] = []
    for img in images:
        start = time.time()
        contents = await img.read()
        if len(contents) > _MAX_BYTES:
            continue
        name = f"{uuid.uuid4().hex}_{img.filename or 'shelf.jpg'}"
        path = _UPLOAD_ROOT / name
        path.write_bytes(contents)
        overall = round(min(100.0, max(5.0, len(contents) / 50000)), 1)
        proc_ms = int((time.time() - start) * 1000) + 5
        scan = ShelfScan(
            store_id=store_id,
            aisle_id=aisle_id,
            image_path=str(path),
            scan_type="manual_upload",
            timestamp=datetime.utcnow(),
            processing_time_ms=proc_ms,
            products_detected=0,
            empty_slots_detected=0,
            overall_occupancy=overall,
            confidence_score=0.8,
            raw_detections=None,
            gemini_summary=None,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)
        analysis = build_mock_analysis(db, scan.id, scan.timestamp, overall, proc_ms)
        scan.products_detected = analysis.products_detected
        scan.empty_slots_detected = analysis.empty_slots
        scan.confidence_score = analysis.confidence_avg
        scan.gemini_summary = analysis.gemini_insight
        db.commit()
        analysis = await _enrich_with_gemini(
            contents, analysis, scan, store_id, aisle_id, db
        )
        results.append(analysis)
    return BatchScanResponse(results=results, total=len(results))


@router.get("/history", response_model=list[ScanHistoryItem])
def scan_history(
    store_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[ScanHistoryItem]:
    q = db.query(ShelfScan).order_by(ShelfScan.timestamp.desc())
    if store_id is not None:
        q = q.filter(ShelfScan.store_id == store_id)
    scans = q.limit(min(limit, 200)).all()
    return [
        ScanHistoryItem(
            scan_id=s.id,
            store_id=s.store_id,
            aisle_id=s.aisle_id,
            timestamp=s.timestamp,
            scan_type=s.scan_type,
            overall_occupancy=s.overall_occupancy,
            products_detected=s.products_detected,
            processing_time_ms=s.processing_time_ms,
        )
        for s in scans
    ]


@router.get("/{scan_id}", response_model=ShelfAnalysisResponse)
def get_scan(scan_id: int, db: Session = Depends(get_db)) -> ShelfAnalysisResponse:
    scan = db.query(ShelfScan).filter(ShelfScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    overall = float(scan.overall_occupancy or 0.0)
    proc = scan.processing_time_ms or 42
    return build_mock_analysis(db, scan.id, scan.timestamp, overall, proc)
