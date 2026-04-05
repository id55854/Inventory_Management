# RetailPulse — local spec pointer

This repo follows **RetailPulse — Technical Specification & Build Guide** (Section 3 directory layout, Section 4 SQLAlchemy models, Section 8 synthetic seed).

Authoritative copy: `RetailPulse_Technical_Spec.md` (same content as the bundled technical spec).

## Section 5 — API (`/api/v1`)

Implemented in `backend/routers/` (`stores`, `scans`, `analytics`, `alerts`, `insights`, `products`). OpenAPI: `http://localhost:8000/docs`.

## Sections 7.1–7.2 — Dashboard UI

Next.js app (`frontend/`): root layout uses `DashboardShell` (sidebar + `Header` + main). Home page (`app/page.tsx`) loads KPI cards, aisle occupancy heatmap (`ShelfHeatmap`), depletion forecast (`StockoutPrediction`), `AlertFeed`, and AI brief. Types in `lib/types.ts`. Set `NEXT_PUBLIC_API_URL` if the API is not on `http://localhost:8000`.

## Section 7.3 — Shelf scan

`app/scan/page.tsx` + `components/scan/ScanWorkspace.tsx`: drag/drop or file input, **Analyze shelf** → `POST /api/v1/scans/upload`, bounding boxes on the image, product list, issues (by severity), Gemini insight, **Generate report** → `POST /api/v1/insights/analyze-shelf`. Toggle **Show/Hide detections**; hover/click syncs list ↔ overlay.

## Section 6.2 — Gemini

Backend `services/gemini.py`: `google.generativeai` with `GEMINI_API_KEY` and optional `GEMINI_MODEL` (default `gemini-2.0-flash`). Wired to `POST /insights/analyze-shelf`, `POST /insights/store-report`, `GET /insights/daily-brief`, and scan upload/batch (narrative `gemini_insight`). Without a key, responses fall back to mocks.
