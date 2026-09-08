from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.ml import forecasting

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
def get_recommendations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db)
    recommendations = []

    if df.empty:
        return {"recommendations": []}

    max_date = df["order_date"].max()
    last_30 = df[df["order_date"] > max_date - timedelta(days=30)]
    prev_30 = df[(df["order_date"] > max_date - timedelta(days=60)) & (df["order_date"] <= max_date - timedelta(days=30))]

    # --- Inventory: forecast trending up strongly ---
    result = forecasting.run_forecast(df, horizon_days=30)
    if result and result.forecast:
        recent_avg = sum(h["revenue"] for h in result.history[-30:]) / max(1, len(result.history[-30:]))
        forecast_avg = sum(f["revenue"] for f in result.forecast) / len(result.forecast)
        if recent_avg > 0 and forecast_avg > recent_avg * 1.1:
            pct = round((forecast_avg / recent_avg - 1) * 100, 1)
            recommendations.append({
                "category": "Inventory",
                "title": "Increase stock ahead of forecasted demand",
                "detail": f"The {result.model_name} model forecasts average daily revenue rising ~{pct}% "
                          f"over the next {len(result.forecast)} days versus the last 30 days. "
                          f"Review stock levels for top-selling products.",
            })

    # --- Marketing: declining categories with strong historical demand ---
    cat_recent = last_30.groupby("category")["revenue"].sum()
    cat_prev = prev_30.groupby("category")["revenue"].sum()
    for cat in cat_prev.index:
        prev_val, recent_val = cat_prev.get(cat, 0), cat_recent.get(cat, 0)
        if prev_val > 0 and recent_val < prev_val * 0.88:
            drop = round((1 - recent_val / prev_val) * 100, 1)
            recommendations.append({
                "category": "Marketing",
                "title": f"Promote {cat}",
                "detail": f"{cat} revenue declined {drop}% in the last 30 days despite strong "
                          f"historical demand (₹{prev_val:,.0f} in the prior period). "
                          f"Consider a targeted promotion or bundle.",
            })

    # --- Customer retention ---
    at_risk_customers = A.top_customers(df[df["segment"] == "At Risk"], n=5)
    if at_risk_customers:
        recommendations.append({
            "category": "Customer Retention",
            "title": "Re-engage at-risk high-value customers",
            "detail": f"{len(A.top_customers(df[df['segment'] == 'At Risk'], n=1000))} customers are "
                      f"classified 'At Risk'. The top 5 by lifetime revenue alone represent "
                      f"₹{sum(c['revenue'] for c in at_risk_customers):,.0f}. Consider a win-back campaign.",
        })

    # --- Regional strategy ---
    growth = A.growth_by_region(df)
    if growth:
        best = growth[0]
        if best["growth_pct"] > 5:
            recommendations.append({
                "category": "Regional Strategy",
                "title": f"Double down on {best['region']}",
                "detail": f"{best['region']} grew {best['growth_pct']:.1f}% (last 30 vs. prior 30 days), "
                          f"the fastest of any region. Consider shifting marketing spend or inventory allocation here.",
            })
        worst = growth[-1]
        if worst["growth_pct"] < -5:
            recommendations.append({
                "category": "Regional Strategy",
                "title": f"Investigate {worst['region']} slowdown",
                "detail": f"{worst['region']} revenue fell {abs(worst['growth_pct']):.1f}% "
                          f"(last 30 vs. prior 30 days). Review regional sales operations and local demand shifts.",
            })

    return {"recommendations": recommendations}
