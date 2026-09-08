from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.api.dashboard_router import _filters

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("")
def list_customers(filters: dict = Depends(_filters), db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db, **filters)
    return {
        "summary": A.customer_summary(df),
        "segments": A.customer_segments(df),
        "top_customers": A.top_customers(df, n=20),
    }


@router.get("/{customer_id}")
def customer_detail(customer_id: int, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=404, detail="No data available.")
    cust_df = df[df["customer_id"] == customer_id]
    if cust_df.empty:
        raise HTTPException(status_code=404, detail="Customer not found.")

    return {
        "customer_name": cust_df["customer_name"].iloc[0],
        "segment": cust_df["segment"].iloc[0],
        "total_revenue": round(float(cust_df["revenue"].sum()), 2),
        "orders": int(cust_df["order_id"].nunique()),
        "avg_order_value": round(float(cust_df["revenue"].sum() / cust_df["order_id"].nunique()), 2),
        "top_products": A.top_products(cust_df, n=5),
    }
