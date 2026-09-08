# Deployment Guide

## Local Development

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # edit as needed (SQLite works with no changes)
python -m app.seed              # loads sample data + creates demo login
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000
npm run dev
```
Visit `http://localhost:5173`.

### Or, everything via Docker Compose
```bash
docker compose up --build
docker compose exec backend python -m app.seed
```
Frontend: `http://localhost:5173` · Backend: `http://localhost:8000`

---

## GitHub

```bash
cd AI-Sales-Analytics
git init
git add .
git commit -m "Initial commit: AI-Powered Sales Analytics & Forecasting Platform"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```
`.env` files are excluded by `.gitignore` — never commit real secrets.

---

## Frontend Deployment (Vercel)

1. Import the GitHub repo into Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite.
4. Environment variable: `VITE_API_URL` = your deployed backend URL (e.g. `https://your-backend.onrender.com`).
5. Deploy.

## Backend Deployment (Render)

1. New → Web Service → connect the GitHub repo.
2. **Root Directory**: `backend`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment variables (Render dashboard):
   - `DATABASE_URL` — from your Render/other PostgreSQL instance
   - `JWT_SECRET` — a long random string
   - `LLM_API_KEY` — optional
   - `LLM_MODEL`, `LLM_PROVIDER` — optional
   - `FRONTEND_URL` — your deployed Vercel URL (for CORS)
6. After first deploy, run the seed script once via Render's shell:
   `python -m app.seed`

### Backend Deployment (Railway) — alternative
1. New Project → Deploy from GitHub repo, set root to `backend`.
2. Add a PostgreSQL plugin; Railway injects `DATABASE_URL` automatically (rename/map to match `DATABASE_URL` if needed).
3. Set the same environment variables as above.
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## PostgreSQL Deployment

Any managed PostgreSQL works (Render PostgreSQL, Railway PostgreSQL, Supabase,
Neon, etc.). Just set `DATABASE_URL` to:
```
postgresql://<user>:<password>@<host>:<port>/<database>
```
Tables are created automatically on backend startup (`Base.metadata.create_all`).
Run `python -m app.seed` once against production to load the sample dataset
and create the demo account (optional — real usage should upload real data
via the Upload page instead).

## Environment Variables Summary

| Variable | Where | Required | Notes |
|----------|-------|----------|-------|
| `DATABASE_URL` | backend | Yes | `sqlite:///./sales_analytics.db` locally, PostgreSQL URL in production |
| `JWT_SECRET` | backend | Yes | Long random string in production |
| `JWT_ALGORITHM` | backend | No | Default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | backend | No | Default `1440` |
| `LLM_API_KEY` | backend | No | Enables full LLM explanations; app works without it |
| `LLM_MODEL` | backend | No | Default `claude-sonnet-4-6` |
| `LLM_PROVIDER` | backend | No | Default `anthropic` |
| `FRONTEND_URL` | backend | Yes (prod) | For CORS |
| `MAX_UPLOAD_SIZE_MB` | backend | No | Default `25` |
| `VITE_API_URL` | frontend | Yes | Points to the deployed backend |

## Final Production Testing Checklist

- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] Register + login works against production DB
- [ ] Dashboard loads with real KPIs
- [ ] Upload a CSV and see it processed
- [ ] Forecast page returns real metrics (not an error)
- [ ] Anomalies page loads
- [ ] AI Analyst answers (with or without `LLM_API_KEY`)
- [ ] CORS: frontend can call backend without browser console errors
