# RetailPulse — Inventory Management (prototype)

- **Backend:** `backend/` — FastAPI, SQLAlchemy, SQLite (`backend/retailpulse.db`).
- **Frontend:** Next.js 14 app in `frontend/` (`npm install` then `npm run dev`).

API (local): `http://localhost:8000/api/v1` · OpenAPI: `http://localhost:8000/docs`

## Environment

- **Backend:** copy `../.env.example` to `backend/.env` and set `GEMINI_API_KEY` (and optional `GEMINI_MODEL`). The app loads `backend/.env` via `python-dotenv` + Pydantic.
- **Frontend:** optional `frontend/.env.local` with `NEXT_PUBLIC_API_URL` pointing at your deployed API (defaults to `http://localhost:8000`).

## Vercel (frontend)

This repo is a monorepo. Deploy the **Next.js** app only:

1. Push this repo to GitHub (see below).
2. In [Vercel](https://vercel.com) → **Add New Project** → import `id55854/Inventory_Management`.
3. Set **Root Directory** to `frontend`.
4. Add env var **`NEXT_PUBLIC_API_URL`** = your public FastAPI base URL (no trailing slash), e.g. `https://your-api.onrender.com` — the FastAPI backend must be hosted separately (Render, Railway, Fly.io, etc.) and allow CORS from your Vercel domain.

The FastAPI backend is **not** deployed by this Vercel project; only `frontend/` is built.

## GitHub

```bash
git init
git add .
git commit -m "Initial RetailPulse monorepo"
git branch -M main
git remote add origin https://github.com/id55854/Inventory_Management.git
git push -u origin main
```

Use a [GitHub personal access token](https://github.com/settings/tokens) or SSH if HTTPS push asks for credentials.
