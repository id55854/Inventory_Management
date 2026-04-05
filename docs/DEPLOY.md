# Deploy RetailPulse (full stack)

You deploy **two pieces**:

| Piece | What | Typical host |
|--------|------|----------------|
| **API** | FastAPI in `backend/` | Render, Railway, Fly.io, Google Cloud Run |
| **Web** | Next.js in `frontend/` | **Vercel** (recommended) |

The browser only talks to the **public URL of the API**. Set `NEXT_PUBLIC_API_URL` on Vercel to that URL (no trailing slash).

---

## 1. Deploy the API (backend)

### Option A — Render (Docker, good for this repo)

1. Push your code to GitHub (e.g. `id55854/Inventory_Management`).
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New +** → **Blueprint** (or **Web Service**).
3. Connect the repo. If using **Web Service** manually:
   - **Root Directory:** `backend`
   - **Environment:** **Docker**
   - **Dockerfile Path:** `backend/Dockerfile` (or leave default if root is `backend`)
   - **Docker Build Context:** `backend` (same folder as the Dockerfile)
4. **Environment variables** (Render → your service → **Environment**):
   | Name | Value |
   |------|--------|
   | `GEMINI_API_KEY` | Your key from [Google AI Studio](https://aistudio.google.com/apikey) |
   | `GEMINI_MODEL` | Optional, default `gemini-2.0-flash` |
5. **Deploy.** When it finishes, copy the service URL, e.g. `https://retailpulse-api-xxxx.onrender.com`.
6. Test: open `https://YOUR-API-URL/docs` — you should see FastAPI Swagger.

**Note:** This app uses **SQLite** on disk. On Render, the disk is **ephemeral** (data can reset on redeploy). For a serious production DB, use PostgreSQL and set `DATABASE_URL` (would require a small code change to use it).

### Option B — Render (native Python, no Docker)

1. **New** → **Web Service** → connect repo.
2. **Root Directory:** `backend`
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Runtime:** Python 3.11 (match `Dockerfile` / your venv).
6. Add the same env vars as above (`GEMINI_API_KEY`, etc.).

### Option C — Railway / Fly.io

- **Railway:** New project → Deploy from GitHub → set root to `backend` → start command `uvicorn main:app --host 0.0.0.0 --port $PORT` → add env vars.
- **Fly.io:** `fly launch` from `backend/` with a `Dockerfile` that uses `PORT` (this repo’s Dockerfile does).

---

## 2. Deploy the frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → **Add New…** → **Project**.
2. **Import** your GitHub repo `Inventory_Management`.
3. **Configure project:**
   - **Framework Preset:** Next.js (auto).
   - **Root Directory:** click **Edit** → set to **`frontend`**.
   - **Build Command:** `npm run build` (default).
   - **Output:** Next.js default (`.next`).
4. **Environment Variables** (important):

   | Name | Value | Environment |
   |------|--------|-------------|
   | `NEXT_PUBLIC_API_URL` | `https://YOUR-API-URL` | Production, Preview, Development |

   Use the **exact** API origin from step 1 — **no** trailing slash.  
   Example: `https://retailpulse-api-xxxx.onrender.com`

5. **Deploy.** After the build, open the Vercel URL. The dashboard will call `NEXT_PUBLIC_API_URL` from the browser.

**CORS:** The FastAPI app already allows `allow_origins=["*"]`, so Vercel preview/production domains work without extra backend config.

---

## 3. Verify end-to-end

1. `GET https://YOUR-API/health` → `{"status":"ok"}`.
2. `GET https://YOUR-API/docs` → Swagger UI.
3. Open your **Vercel** site → home dashboard should load store data (if the API is up).
4. If the UI shows errors, check the browser **Network** tab: failed calls to the API usually mean wrong `NEXT_PUBLIC_API_URL` or the API is sleeping (Render free tier spins down — first request can be slow).

---

## 4. Optional: `render.yaml` in this repo

If you use Render **Blueprint**, you can commit `render.yaml` at the repo root and Render will propose a service from it. Adjust names/URLs after the first deploy.

---

## 5. Secrets checklist

- **Never commit** `backend/.env` (it is gitignored).
- Set `GEMINI_API_KEY` only in the **hosting dashboard** (Render/Vercel/Railway), not in the repo.
- Rotate keys if they were ever committed or pasted in chat.

---

## 6. Local vs production

| | Local | Production |
|---|--------|------------|
| API | `http://localhost:8000` | `https://your-api-host` |
| Frontend env | Optional `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000` | Vercel: `NEXT_PUBLIC_API_URL=https://your-api-host` |
| Gemini | `backend/.env` | Host env vars on the API service |

---

## 7. Vercel monorepo: root vs `frontend/`

### `package.json` not found at repo root

If the build log shows **`Could not read package.json`** under `/vercel/path0/package.json`, the project was building from the **monorepo root** without seeing the Next app.

1. **Preferred:** Vercel → **Project** → **Settings** → **General** → **Root Directory** → **`frontend`** → save → **Redeploy**.
2. The repo also ships a root **`package.json`** and **`vercel.json`** so install/build run inside **`frontend/`** when Root Directory is left blank.

### `routes-manifest.json` could not be found

If **`next build` succeeds** but deployment fails with **`.next/routes-manifest.json` missing** at the repo root, Vercel’s Next.js step is looking for **`.next`** next to the Git root while the build wrote **`frontend/.next`**.

1. **Preferred:** set **Root Directory** to **`frontend`** (same as above). Then `.next` is under the project root and you do not need the copy step.
2. If Root Directory stays blank, the root **`vercel.json`** runs a post-build copy of **`frontend/.next`** → **`.next`** at the repo root so the builder can find `routes-manifest.json`.
