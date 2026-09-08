# API Documentation

Base URL (local): `http://localhost:8000`
Interactive docs (Swagger): `http://localhost:8000/docs`

All endpoints except `/health`, `/auth/register`, and `/auth/login` require:
`Authorization: Bearer <token>`

## Auth

| Method | Path              | Description                    |
|--------|-------------------|--------------------------------|
| POST   | `/auth/register`  | Create an account, returns JWT |
| POST   | `/auth/login`     | Log in, returns JWT            |
| GET    | `/auth/me`        | Current user info              |

## Upload

| Method | Path                    | Description                              |
|--------|-------------------------|-------------------------------------------|
| POST   | `/upload`               | Upload CSV/Excel (multipart form, field `file`) |
| GET    | `/upload/status/{id}`   | Check status of a past upload job         |

## Dashboard

| Method | Path                        | Description                          |
|--------|-----------------------------|---------------------------------------|
| GET    | `/dashboard/summary`        | KPIs + all main chart series          |
| GET    | `/dashboard/revenue`        | Revenue/profit/orders time series     |
| GET    | `/dashboard/profit`         | Profit broken down by category/region |
| GET    | `/dashboard/insights`       | AI-generated business insights        |
| GET    | `/dashboard/filter-options` | Valid values for region/category/segment/product filters |

All dashboard/products/customers/regions endpoints accept these optional
query filters: `start_date`, `end_date`, `region`, `category`, `product_id`,
`segment`.

## Products / Customers / Regions

| Method | Path                    | Description                    |
|--------|-------------------------|---------------------------------|
| GET    | `/products`             | Full product performance table  |
| GET    | `/products/{id}`        | Single product detail + trend   |
| GET    | `/customers`            | Segments, summary, top customers|
| GET    | `/customers/{id}`       | Single customer detail          |
| GET    | `/regions`              | Revenue/profit/growth by region |

## Forecast

| Method | Path                | Description                                    |
|--------|---------------------|-------------------------------------------------|
| GET    | `/forecast?horizon=` | 7/30/90-day forecast + model comparison metrics |
| GET    | `/forecast/metrics`  | Just the model comparison table (MAE/RMSE/MAPE) |

## Anomalies

| Method | Path                        | Description                       |
|--------|-----------------------------|-------------------------------------|
| GET    | `/anomalies?severity=`      | Isolation Forest anomalies, optional severity filter (Low/Medium/High) |

## AI Analyst

| Method | Path            | Description                                          |
|--------|-----------------|-------------------------------------------------------|
| POST   | `/ai/chat`      | Body: `{"question": "..."}`. Returns a grounded answer |
| GET    | `/ai/insights`  | Same insights shown on the dashboard                  |
| GET    | `/ai/status`    | Whether an LLM key is configured                      |

## Recommendations

| Method | Path                | Description                                      |
|--------|---------------------|----------------------------------------------------|
| GET    | `/recommendations`  | Inventory/marketing/retention/regional suggestions |

## Health

| Method | Path      | Description                          |
|--------|-----------|---------------------------------------|
| GET    | `/health` | `{"status": "ok", "ai_configured": bool}` |
