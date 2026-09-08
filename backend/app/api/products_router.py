from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.api.dashboard_router import _filters

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(filters: dict = Depends(_filters), db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db, **filters)
    return {"products": A.product_table(df)}


@router.get("/{product_id}")
def product_detail(product_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available.")
    prod_df = df[df["product_id"] == product_id]
    if prod_df.empty:
        raise HTTPException(status_code=404, detail="Product not found.")

    days_span = (df["order_date"].max() - df["order_date"].min()).days
    return {
        "product_name": prod_df["product_name"].iloc[0],
        "category": prod_df["category"].iloc[0],
        "total_revenue": round(float(prod_df["revenue"].sum()), 2),
        "total_profit": round(float(prod_df["profit"].sum()), 2),
        "units_sold": int(prod_df["quantity"].sum()),
        "orders": int(prod_df["order_id"].nunique()),
        "revenue_over_time": A.revenue_over_time(prod_df, freq="D" if days_span <= 120 else "W"),
        "revenue_by_region": A.revenue_by_region(prod_df),
    }
