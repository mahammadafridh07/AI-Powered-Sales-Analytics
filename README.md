# AI-Powered Sales Analytics & Forecasting Platform

A full-stack, portfolio-ready analytics platform: upload sales data, explore
executive dashboards, get ML-driven forecasts and anomaly detection, and ask
an AI Sales Analyst plain-English questions — all grounded in your real data.

## Overview

Built as a complete, runnable project (not a demo): FastAPI + PostgreSQL/SQLite
backend with real pandas/scikit-learn/XGBoost analytics and forecasting, and a
React + TypeScript + Tailwind frontend. Ships with a realistic 3-year, ~29,600-row
sample dataset so it works immediately after setup.

## Features

- JWT authentication (register/login/logout, protected routes)
- CSV/Excel upload with validation, cleaning, and error handling
- Executive dashboard: KPIs, revenue/profit trends, category/region breakdowns, filters
- Product, customer, and regional analytics
- Sales forecasting: Random Forest & XGBoost trained and validated against a
  seasonal-naive baseline; best model auto-selected by MAPE; real MAE/RMSE/MAPE
- Anomaly detection via Isolation Forest, with severity scoring
- AI Sales Analyst: safe, read-only analytics query layer + LLM explanation,
  with a graceful, still-accurate fallback when no LLM key is configured
- Data-driven recommendations (inventory, marketing, retention, regional)
- Dark/light mode, responsive layout, loading/empty/error states throughout

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full breakdown.
Short version: React SPA → FastAPI (analytics/ml/ai layers) → PostgreSQL/SQLite.
The AI Analyst never touches the database directly — it only receives
pre-computed, verified JSON from a safe analytics layer.

## Tech Stack

**Frontend:** React 19, Vite, TypeScript, Tailwind CSS v4, Recharts, Lucide, React Router, Axios
**Backend:** FastAPI, SQLAlchemy, Pydantic, python-jose (JWT), bcrypt
**Data/ML:** pandas, NumPy, scikit-learn (Random Forest, Isolation Forest), XGBoost
**AI:** Anthropic API (optional, via `LLM_API_KEY`)
**Database:** PostgreSQL (production) / SQLite (local dev, zero setup)
**Deployment:** Vercel (frontend), Render/Railway (backend), Docker Compose (all-in-one local)

## Project Structure

```
AI-Sales-Analytics/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── analytics/      # Safe, read-only analytics engine
│   │   ├── ml/              # Forecasting + anomaly detection
│   │   ├── ai/               # AI Sales Analyst service
│   │   ├── services/        # Auth + upload/ingestion
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── database/         # DB session/engine
│   │   ├── main.py
│   │   └── seed.py
│   ├── tests/                # pytest suite (27 tests)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/            # Landing, Login, Register, Dashboard, ...
│   │   ├── components/       # AppShell, FilterBar, UI primitives
│   │   ├── context/          # Auth + Theme providers
│   │   └── lib/api.ts
│   └── Dockerfile
├── data/
│   ├── sample_sales.csv
│   └── generate_sample_data.py
├── database/
│   ├── schema.sql
│   └── seed.sql
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## Installation & Running Locally

### 1. Backend
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python -m app.seed          # seeds sample data + demo login
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

### Or with Docker Compose
```bash
docker compose up --build
docker compose exec backend python -m app.seed
```

## Environment Variables

See `.env.example` (backend) and `frontend/.env.example`. Full reference in
[`docs/deployment.md`](docs/deployment.md). The app works with zero
configuration beyond copying `.env.example` — SQLite and no LLM key are valid
defaults.

## Demo Login

```
Email:    demo@salesai.com
Password: Demo@1234
```
(Created automatically by `python -m app.seed`.)

## Database Setup

Tables are created automatically on backend startup via SQLAlchemy. See
`database/schema.sql` for the equivalent raw PostgreSQL DDL (for reference/
interview walkthroughs) and `database/seed.sql` for a note on how seeding
actually works (via `app/seed.py`, not static inserts).

## Using the Application

1. Log in with the demo account (or register a new one).
2. The dashboard is already populated from the seeded sample data.
3. Explore Products / Customers / Regions / Forecast / Anomalies / AI Analyst / Recommendations.
4. Optionally upload your own CSV/Excel file from the Upload page — required
   columns: `order_date, customer_id, customer_name, region, product_id,
   product_name, category, quantity, unit_price, revenue, profit`
   (`segment`, `subcategory`, `salesperson`, `order_status`, `discount` optional).

## ML Pipeline & Forecasting Methodology

Daily revenue is aggregated, feature-engineered (lags, rolling means,
day-of-week/month, time index), split by TIME (last 20% held out — never
randomly shuffled, which would leak the future into training). A seasonal-naive
baseline, Random Forest, and XGBoost are all trained and scored on the same
held-out window using MAE/RMSE/MAPE; the lowest-MAPE model is refit on all
data and rolled forward autoregressively for the requested horizon (7/30/90
days). See `backend/app/ml/forecasting.py`.

## AI Architecture

```
User Question → Intent detection (keyword/heuristic, no LLM call needed)
              → Safe analytics query (app/analytics/engine.py function call)
              → Structured JSON result
              → LLM explanation (only if LLM_API_KEY is set)
              → Grounded answer + recommendation
```
The LLM never receives database credentials or raw SQL access — only the
pre-computed result. See `backend/app/ai/ai_service.py`.

## API Documentation

See [`docs/api.md`](docs/api.md), or run the backend and visit `/docs` for
live Swagger UI.

## Testing

```bash
cd backend
pip install -r requirements.txt   # includes pytest
python -m pytest tests/ -v
```
27 tests covering auth, upload validation/cleaning, analytics, forecasting
(real metrics, not mocks), anomaly detection, and the AI Analyst's
no-key fallback path.

## Deployment

Full steps in [`docs/deployment.md`](docs/deployment.md): Vercel (frontend),
Render/Railway (backend), managed PostgreSQL, plus a one-command
`docker compose up` path for running everything locally.

## Troubleshooting

- **CORS errors in the browser console**: check `FRONTEND_URL` in the backend
  `.env` matches where your frontend is actually running.
- **`ModuleNotFoundError` on backend start**: make sure you're in the
  `backend/` directory and the virtualenv is activated before `pip install`.
- **Forecast/anomalies return an error**: they need a minimum amount of
  history (40+ days / 30+ rows) — seed the sample data first if testing fresh.
- **bcrypt/passlib errors**: this project uses `bcrypt` directly (not
  `passlib`) to avoid a known incompatibility with bcrypt 5.x.

## Future Improvements

- Product/customer detail pages with deep-linkable drill-down views
- CSV export of filtered analytics tables
- Role-based access control (admin vs. viewer)
- Alembic migrations instead of `create_all` for schema evolution
- WebSocket-based upload progress instead of simulated stage timing

## Author

Built as a portfolio project demonstrating full-stack development, applied
data analytics, ML forecasting/anomaly detection, and safe LLM integration.

## Known Limitations

- Upload pipeline progress bar shows a short simulated animation alongside
  the real request rather than true server-sent progress events.
- Regional visualization is a comparison view, not a geographic map (by design,
  to avoid extra mapping-API deployment complexity — see project spec §16).
- Forecast confidence bands are based on validation residual standard
  deviation (a reasonable, explainable approximation), not full Bayesian
  posterior intervals.
