from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import User
from app.services.auth_service import get_current_user
from app.analytics import engine as A
from app.api.dashboard_router import _filters

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("")
def list_regions(filters: dict = Depends(_filters), db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    df = A.load_dataframe(db, **filters)
    revenue = A.revenue_by_region(df)
    growth = A.growth_by_region(df)
    growth_map = {g["region"]: g["growth_pct"] for g in growth}

    top_products_by_region = {}
    if not df.empty:
        for region in df["region"].dropna().unique():
            region_df = df[df["region"] == region]
            top_products_by_region[region] = A.top_products(region_df, n=3)

    for row in revenue:
        row["growth_pct"] = growth_map.get(row["region"], 0.0)
        row["top_products"] = top_products_by_region.get(row["region"], [])

    return {"regions": revenue}
