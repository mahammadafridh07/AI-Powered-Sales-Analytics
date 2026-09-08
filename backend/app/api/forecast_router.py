from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.ml import forecasting

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("")
def get_forecast(
    horizon: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df = A.load_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=400, detail="No sales data available. Upload data first.")

    result = forecasting.run_forecast(df, horizon_days=horizon)
    if result is None:
        raise HTTPException(status_code=400,
                             detail="Not enough historical data to generate a reliable forecast (need 40+ days).")

    return {
        "model_used": result.model_name,
        "metrics": result.metrics,
        "history": result.history,
        "forecast": result.forecast,
        "horizon_days": horizon,
        "expected_revenue_total": round(sum(f["revenue"] for f in result.forecast), 2),
    }


@router.get("/metrics")
def forecast_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=400, detail="No sales data available. Upload data first.")
    result = forecasting.run_forecast(df, horizon_days=7)
    if result is None:
        raise HTTPException(status_code=400, detail="Not enough historical data to evaluate models.")
    return {"model_used": result.model_name, "metrics": result.metrics}
