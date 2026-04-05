# RetailPulse — Inventory Management (prototype)

- **Backend:** `backend/` — FastAPI, SQLAlchemy, SQLite (`backend/retailpulse.db`).
- **Frontend:** Next.js 14 app in `frontend/` (`npm install` then `npm run dev`).

API (local): `http://localhost:8000/api/v1` · OpenAPI: `http://localhost:8000/docs`

## Environment

- **Backend:** copy `../.env.example` to `backend/.env` and set `GEMINI_API_KEY` (and optional `GEMINI_MODEL`). The app loads `backend/.env` via `python-dotenv` + Pydantic.
- **Frontend:** optional `frontend/.env.local` with `NEXT_PUBLIC_API_URL` pointing at your deployed API (defaults to `http://localhost:8000`).

## GitHub

Repository: **https://github.com/id55854/Inventory_Management**

Clone and push updates:

```bash
git remote add origin https://github.com/id55854/Inventory_Management.git   # if not set
git push -u origin main
```

Use a [GitHub personal access token](https://github.com/settings/tokens) or SSH if HTTPS push asks for credentials.

## Vercel (frontend)

This repo is a monorepo. Only the **Next.js** app in `frontend/` is deployed to Vercel; the FastAPI API must run elsewhere (Render, Railway, Fly.io, etc.) with CORS enabled.

### Option A — Import from GitHub (recommended for CI)

1. [Vercel](https://vercel.com) → **Add New Project** → import **id55854/Inventory_Management**.
2. **Root Directory:** `frontend`.
3. **Environment variables:** `NEXT_PUBLIC_API_URL` = your public API origin (no trailing slash), e.g. `https://your-api.onrender.com`.

### Option B — CLI deploy (already linked)

A production deployment was created from this machine; stable alias:

- **https://frontend-jet-tau-16.vercel.app**

Set `NEXT_PUBLIC_API_URL` in the Vercel project **Settings → Environment Variables** so the dashboard can reach your API.

The FastAPI backend is **not** built by this Vercel project; deploy `backend/` separately or use Docker.

**Step-by-step (API + Vercel + env vars):** see **[docs/DEPLOY.md](docs/DEPLOY.md)**.  
Quick backend option: connect the repo to [Render](https://render.com) and use **`render.yaml`** at the repo root (Dockerfile in `backend/`), then set **`GEMINI_API_KEY`** in Render’s dashboard.
