"""
Analytics engine.

All functions here are READ-ONLY aggregations over the order_items/orders/
customers/products tables. They are the *only* way data is retrieved for
both the dashboard REST endpoints and the AI Sales Analyst -- the LLM never
sees raw SQL or the database connection, only the structured dict results
these functions return. This is the "safe query" layer described in the
project spec.
"""

from datetime import date, timedelta
from typing import Optional
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Order, OrderItem, Product, Customer


def _base_query(db: Session):
    return (
        select(
            OrderItem.id, OrderItem.quantity, OrderItem.unit_price, OrderItem.discount,
            OrderItem.revenue, OrderItem.profit,
            Order.order_id, Order.order_date, Order.region, Order.order_status, Order.salesperson,
            Product.product_id, Product.product_name, Product.category, Product.subcategory,
            Customer.customer_id, Customer.name.label("customer_name"), Customer.segment,
        )
        .join(Order, Order.order_id == OrderItem.order_id)
        .join(Product, Product.product_id == OrderItem.product_id)
        .join(Customer, Customer.customer_id == Order.customer_id)
    )


def load_dataframe(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    product_id: Optional[int] = None,
    segment: Optional[str] = None,
    exclude_cancelled: bool = True,
) -> pd.DataFrame:
    """Load filtered order-item-level data into a DataFrame for analysis."""
    q = _base_query(db)
    if start_date:
        q = q.where(Order.order_date >= start_date)
    if end_date:
        q = q.where(Order.order_date <= end_date)
    if region:
        q = q.where(Order.region == region)
    if category:
        q = q.where(Product.category == category)
    if product_id:
        q = q.where(Product.product_id == product_id)
    if segment:
        q = q.where(Customer.segment == segment)
    if exclude_cancelled:
        q = q.where(Order.order_status != "Cancelled")

    rows = db.execute(q).all()
    df = pd.DataFrame(rows, columns=[
        "id", "quantity", "unit_price", "discount", "revenue", "profit",
        "order_id", "order_date", "region", "order_status", "salesperson",
        "product_id", "product_name", "category", "subcategory",
        "customer_id", "customer_name", "segment",
    ])
    if not df.empty:
        df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def kpi_summary(df: pd.DataFrame, previous_df: pd.DataFrame) -> dict:
    def growth(curr, prev):
        if prev == 0:
            return 0.0
        return round(((curr - prev) / prev) * 100, 2)

    revenue = float(df["revenue"].sum())
    profit = float(df["profit"].sum())
    orders = int(df["order_id"].nunique())
    customers = int(df["customer_id"].nunique())
    aov = round(revenue / orders, 2) if orders else 0.0

    prev_revenue = float(previous_df["revenue"].sum())
    prev_profit = float(previous_df["profit"].sum())
    prev_orders = int(previous_df["order_id"].nunique())
    prev_customers = int(previous_df["customer_id"].nunique())
    prev_aov = round(prev_revenue / prev_orders, 2) if prev_orders else 0.0

    return {
        "revenue": {"value": round(revenue, 2), "growth_pct": growth(revenue, prev_revenue)},
        "profit": {"value": round(profit, 2), "growth_pct": growth(profit, prev_profit)},
        "orders": {"value": orders, "growth_pct": growth(orders, prev_orders)},
        "avg_order_value": {"value": aov, "growth_pct": growth(aov, prev_aov)},
        "customers": {"value": customers, "growth_pct": growth(customers, prev_customers)},
    }


def revenue_over_time(df: pd.DataFrame, freq: str = "D") -> list:
    if df.empty:
        return []
    s = df.set_index("order_date").resample(freq).agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
                                                        orders=("order_id", "nunique"))
    s = s.reset_index()
    s["order_date"] = s["order_date"].dt.strftime("%Y-%m-%d")
    return s.to_dict(orient="records")


def revenue_by_category(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    g = df.groupby("category").agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
                                    orders=("order_id", "nunique")).reset_index()
    return g.sort_values("revenue", ascending=False).round(2).to_dict(orient="records")


def revenue_by_region(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    g = df.groupby("region").agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
                                  orders=("order_id", "nunique")).reset_index()
    return g.sort_values("revenue", ascending=False).round(2).to_dict(orient="records")


def top_products(df: pd.DataFrame, n: int = 10, ascending: bool = False) -> list:
    if df.empty:
        return []
    g = df.groupby(["product_id", "product_name", "category"]).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"),
        units_sold=("quantity", "sum"), orders=("order_id", "nunique"),
    ).reset_index()
    return g.sort_values("revenue", ascending=ascending).head(n).round(2).to_dict(orient="records")


def product_table(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    g = df.groupby(["product_id", "product_name", "category"]).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"),
        units_sold=("quantity", "sum"), orders=("order_id", "nunique"),
        avg_discount=("discount", "mean"),
    ).reset_index()
    g["margin_pct"] = (g["profit"] / g["revenue"] * 100).round(2)
    return g.round(2).sort_values("revenue", ascending=False).to_dict(orient="records")


def customer_segments(df: pd.DataFrame) -> list:
    if df.empty:
        return []
    g = df.groupby("segment").agg(
        revenue=("revenue", "sum"), customers=("customer_id", "nunique"), orders=("order_id", "nunique"),
    ).reset_index()
    g["avg_order_value"] = (g["revenue"] / g["orders"]).round(2)
    return g.round(2).sort_values("revenue", ascending=False).to_dict(orient="records")


def top_customers(df: pd.DataFrame, n: int = 10) -> list:
    if df.empty:
        return []
    g = df.groupby(["customer_id", "customer_name", "segment"]).agg(
        revenue=("revenue", "sum"), orders=("order_id", "nunique"),
    ).reset_index()
    g["avg_order_value"] = (g["revenue"] / g["orders"]).round(2)
    return g.sort_values("revenue", ascending=False).head(n).round(2).to_dict(orient="records")


def customer_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total_customers": 0, "new_customers": 0, "returning_customers": 0, "avg_order_value": 0}
    orders_per_customer = df.groupby("customer_id")["order_id"].nunique()
    returning = int((orders_per_customer > 1).sum())
    new = int((orders_per_customer == 1).sum())
    revenue = float(df["revenue"].sum())
    orders = int(df["order_id"].nunique())
    return {
        "total_customers": int(df["customer_id"].nunique()),
        "new_customers": new,
        "returning_customers": returning,
        "avg_order_value": round(revenue / orders, 2) if orders else 0,
    }


def growth_by_region(df: pd.DataFrame) -> list:
    """Compares latest 30 days vs prior 30 days per region."""
    if df.empty:
        return []
    max_date = df["order_date"].max()
    recent_cut = max_date - timedelta(days=30)
    prior_cut = max_date - timedelta(days=60)

    recent = df[df["order_date"] > recent_cut].groupby("region")["revenue"].sum()
    prior = df[(df["order_date"] > prior_cut) & (df["order_date"] <= recent_cut)].groupby("region")["revenue"].sum()

    regions = sorted(set(recent.index) | set(prior.index))
    out = []
    for r in regions:
        rec = float(recent.get(r, 0))
        pri = float(prior.get(r, 0))
        growth = ((rec - pri) / pri * 100) if pri else 0.0
        out.append({"region": r, "recent_30d_revenue": round(rec, 2),
                     "prior_30d_revenue": round(pri, 2), "growth_pct": round(growth, 2)})
    return sorted(out, key=lambda x: x["growth_pct"], reverse=True)
