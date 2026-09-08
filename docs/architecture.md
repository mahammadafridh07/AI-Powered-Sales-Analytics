# Architecture

## Overview

A monolithic-but-clean architecture: one FastAPI backend, one React frontend,
one relational database. No microservices, no message queues, no Kubernetes —
deliberately, per the project's "don't overengineer" requirement.

```
┌─────────────┐      HTTPS/JSON      ┌──────────────┐      SQL       ┌────────────┐
│   React SPA │ ───────────────────▶ │   FastAPI    │ ─────────────▶ │ PostgreSQL │
│  (Vite, TS) │ ◀─────────────────── │   Backend    │ ◀───────────── │ (or SQLite)│
└─────────────┘                      └──────┬───────┘                └────────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                        pandas/sklearn   Isolation      Anthropic API
                        forecasting      Forest          (optional)
                        (RF / XGBoost)   anomalies
```

## Backend layers

- **api/** — FastAPI routers. Thin: parse request, call a service/analytics
  function, return a schema. No business logic here.
- **analytics/engine.py** — The single, safe, read-only query layer. Every
  chart, KPI, and AI answer is produced by calling a function here. This is
  what stands between the AI layer and the raw database.
- **ml/** — `forecasting.py` (model training + comparison + rolling forecast)
  and `anomaly_detection.py` (Isolation Forest).
- **ai/ai_service.py** — Intent detection → calls `analytics.engine` →
  optionally sends the *result* (never raw SQL, never the DB connection) to
  an LLM for explanation. Falls back to a deterministic, data-grounded
  template answer if no `LLM_API_KEY` is configured.
- **services/** — Auth (JWT + bcrypt) and upload/ingestion (validate → clean
  → store).
- **models/** — SQLAlchemy ORM models (the source of truth for the schema;
  `database/schema.sql` mirrors it for reference).

## Frontend layers

- **pages/** — One file per route/page.
- **components/** — `AppShell` (sidebar/topbar), `FilterBar`, and small
  reusable UI primitives (`UI.tsx`).
- **context/** — `AuthContext` (JWT + user in localStorage) and
  `ThemeContext` (dark/light, class-based Tailwind v4 dark mode).
- **lib/api.ts** — Axios instance with an interceptor that attaches the JWT
  and redirects to `/login` on 401.

## Why this design

- **Safe AI architecture**: the LLM never has DB credentials or the ability
  to generate arbitrary SQL. It only ever receives pre-computed, verified
  JSON from `analytics.engine`, which makes destructive operations
  structurally impossible, not just prompt-forbidden.
- **Model comparison, not model guessing**: forecasting always trains and
  validates multiple models on a held-out time window and reports real
  MAE/RMSE/MAPE before picking a winner — nothing is hardcoded.
- **Works with zero configuration**: SQLite + no LLM key + bundled sample
  data means `python -m app.seed && uvicorn app.main:app` is enough to see
  the full product working end to end.
