"""
Handles ingesting an uploaded sales CSV/Excel file:
  validate -> clean -> load into the relational tables (customers, products,
  orders, order_items). Designed to never crash on bad input -- validation
  errors are collected and returned to the user instead of raising 500s.
"""

from datetime import datetime
from typing import Tuple
import io
import pandas as pd
from sqlalchemy.orm import Session

from app.models.models import Customer, Product, Order, OrderItem

REQUIRED_COLUMNS = [
    "order_date", "customer_id", "customer_name", "region", "product_id",
    "product_name", "category", "quantity", "unit_price", "revenue", "profit",
]

OPTIONAL_DEFAULTS = {
    "segment": "Potential", "subcategory": None, "salesperson": "Unassigned",
    "order_status": "Completed", "discount": 0.0,
}


def read_upload(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(file_bytes))
    return pd.read_csv(io.BytesIO(file_bytes))


def validate(df: pd.DataFrame) -> Tuple[bool, list]:
    errors = []
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, errors  # can't continue further checks without columns

    if df.empty:
        errors.append("The uploaded file contains no rows.")
        return False, errors

    # Type / value checks (collect, don't fail immediately -- these become warnings
    # for rows that get dropped during cleaning)
    bad_dates = pd.to_datetime(df["order_date"], errors="coerce").isna().sum()
    if bad_dates:
        errors.append(f"{bad_dates} row(s) have invalid order_date values (will be dropped).")

    for col in ["quantity", "unit_price", "revenue"]:
        non_numeric = pd.to_numeric(df[col], errors="coerce").isna().sum()
        if non_numeric:
            errors.append(f"{non_numeric} row(s) have non-numeric {col} (will be dropped).")

    negative_qty = (pd.to_numeric(df["quantity"], errors="coerce") < 0).sum()
    if negative_qty:
        errors.append(f"{negative_qty} row(s) have negative quantity (will be dropped).")

    dup_count = df.duplicated().sum()
    if dup_count:
        errors.append(f"{dup_count} duplicate row(s) found (will be removed).")

    return True, errors


def clean(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d = d.drop_duplicates()
    d["order_date"] = pd.to_datetime(d["order_date"], errors="coerce")
    d = d.dropna(subset=["order_date"])

    for col in ["quantity", "unit_price", "revenue"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d.dropna(subset=["quantity", "unit_price", "revenue"])
    d = d[d["quantity"] >= 0]

    if "profit" not in d.columns:
        d["profit"] = 0.0
    d["profit"] = pd.to_numeric(d["profit"], errors="coerce").fillna(0)

    if "discount" not in d.columns:
        d["discount"] = 0.0
    d["discount"] = pd.to_numeric(d["discount"], errors="coerce").fillna(0)

    for col, default in OPTIONAL_DEFAULTS.items():
        if col not in d.columns:
            d[col] = default
        elif default is not None:
            d[col] = d[col].fillna(default)
        # else: optional column with no sensible default (e.g. subcategory) --
        # leave any missing values as NaN/None rather than calling fillna(None),
        # which pandas treats as an invalid argument (no value/method specified).

    return d.reset_index(drop=True)


def ingest(db: Session, df: pd.DataFrame) -> int:
    """Upserts customers/products, then inserts orders/order_items.
    Uses simple dict caches to avoid N+1 queries during ingestion."""

    existing_customers = {c.customer_id: c for c in db.query(Customer).all()}
    existing_products = {p.product_id: p for p in db.query(Product).all()}
    existing_orders = set(o.order_id for o in db.query(Order.order_id).all())

    # Upsert customers
    for _, row in df.drop_duplicates("customer_id").iterrows():
        cid = int(row["customer_id"])
        if cid not in existing_customers:
            cust = Customer(
                customer_id=cid, name=str(row.get("customer_name", f"Customer {cid}")),
                region=str(row.get("region", "Unknown")), segment=str(row.get("segment", "Potential")),
            )
            db.add(cust)
            existing_customers[cid] = cust
    db.flush()

    # Upsert products
    for _, row in df.drop_duplicates("product_id").iterrows():
        pid = int(row["product_id"])
        if pid not in existing_products:
            prod = Product(
                product_id=pid, product_name=str(row.get("product_name", f"Product {pid}")),
                category=str(row.get("category", "Uncategorized")),
                subcategory=str(row.get("subcategory") or row.get("category", "Uncategorized")),
                price=float(row["unit_price"]), cost=float(row["unit_price"]) * 0.65,
            )
            db.add(prod)
            existing_products[pid] = prod
    db.flush()

    # Determine order_id column -- if not present, derive one per unique
    # (order_date, customer_id) combination so line items group correctly.
    if "order_id" not in df.columns:
        df = df.copy()
        df["order_id"] = df.groupby(["order_date", "customer_id"]).ngroup() + 1_000_000

    rows_inserted = 0
    for oid, group in df.groupby("order_id"):
        oid = int(oid)
        first = group.iloc[0]
        if oid not in existing_orders:
            order = Order(
                order_id=oid, customer_id=int(first["customer_id"]),
                order_date=first["order_date"].date(), region=str(first.get("region", "Unknown")),
                salesperson=str(first.get("salesperson", "Unassigned")),
                order_status=str(first.get("order_status", "Completed")),
            )
            db.add(order)
            existing_orders.add(oid)

        for _, row in group.iterrows():
            item = OrderItem(
                order_id=oid, product_id=int(row["product_id"]),
                quantity=int(row["quantity"]), unit_price=float(row["unit_price"]),
                discount=float(row.get("discount", 0)), revenue=float(row["revenue"]),
                profit=float(row.get("profit", 0)),
            )
            db.add(item)
            rows_inserted += 1

    db.commit()
    return rows_inserted
