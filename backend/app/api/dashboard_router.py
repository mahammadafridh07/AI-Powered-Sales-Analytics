from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _filters(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    segment: Optional[str] = Query(None),
):
    return dict(start_date=start_date, end_date=end_date, region=region,
                category=category, product_id=product_id, segment=segment)


@router.get("/summary")
def dashboard_summary(
    filters: dict = Depends(_filters),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df = A.load_dataframe(db, **filters)
    if df.empty:
        return {
            "kpis": None, "revenue_over_time": [], "revenue_by_category": [],
            "revenue_by_region": [], "top_products": [], "customer_segments": [],
            "has_data": False,
        }

    # Default comparison window: last 30 days vs prior 30 days (relative to data's own max date,
    # unless the caller has applied an explicit date filter, in which case compare within that window)
    current_period = df
    days_span = (df["order_date"].max() - df["order_date"].min()).days or 30
    half = max(1, days_span // 2)
    mid_point = df["order_date"].max() - timedelta(days=half)
    prev_period = df[df["order_date"] <= mid_point]
    curr_period = df[df["order_date"] > mid_point]

    return {
        "has_data": True,
        "kpis": A.kpi_summary(curr_period if not curr_period.empty else df, prev_period),
        "revenue_over_time": A.revenue_over_time(df, freq="D" if days_span <= 120 else "W"),
        "revenue_by_category": A.revenue_by_category(df),
        "revenue_by_region": A.revenue_by_region(df),
        "top_products": A.top_products(df, n=8),
        "customer_segments": A.customer_segments(df),
    }


@router.get("/revenue")
def dashboard_revenue(filters: dict = Depends(_filters), db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db, **filters)
    days_span = (df["order_date"].max() - df["order_date"].min()).days if not df.empty else 0
    return {"series": A.revenue_over_time(df, freq="D" if days_span <= 120 else "W")}


@router.get("/profit")
def dashboard_profit(filters: dict = Depends(_filters), db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db, **filters)
    return {"by_category": A.revenue_by_category(df), "by_region": A.revenue_by_region(df)}


@router.get("/insights")
async def dashboard_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.ai import ai_service
    insights = await ai_service.generate_insights(db)
    return {"insights": insights}


@router.get("/filter-options")
def filter_options(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db)
    if df.empty:
        return {"regions": [], "categories": [], "segments": [], "products": []}
    return {
        "regions": sorted(df["region"].dropna().unique().tolist()),
        "categories": sorted(df["category"].dropna().unique().tolist()),
        "segments": sorted(df["segment"].dropna().unique().tolist()),
        "products": df[["product_id", "product_name"]].drop_duplicates().sort_values("product_name").to_dict(orient="records"),
    }
