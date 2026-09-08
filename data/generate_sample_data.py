"""
Generates a realistic synthetic sales dataset for the AI Sales Analytics platform.

Design goals (not pure randomness):
- 3 years of daily order activity (2023-01-01 -> 2025-12-31)
- Upward year-over-year revenue trend (~12-18% YoY growth)
- Monthly seasonality (Nov/Dec spike for holidays, summer dip)
- Weekly seasonality (weekend dip for B2B-style categories)
- Category/product level differences in price, margin, popularity
- Regional differences in demand and growth
- Customer segments with different order frequency & value
- A small percentage of injected anomalies (revenue spikes/drops) so
  anomaly detection has real signal to find
- Occasional missing/duplicate rows removed before final export is NOT
  done here -- a separate "dirty" sample could be added later. This file
  produces the CLEAN dataset used to seed the app and power ML.

Output: data/sample_sales.csv  (one row per order line item)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
ALL_DATES = pd.date_range(START_DATE, END_DATE, freq="D")

REGIONS = {
    "North":  {"base_demand": 1.00, "growth": 0.14},
    "South":  {"base_demand": 1.25, "growth": 0.18},
    "East":   {"base_demand": 0.85, "growth": 0.10},
    "West":   {"base_demand": 1.10, "growth": 0.15},
    "Central":{"base_demand": 0.70, "growth": 0.08},
}

STATES_BY_REGION = {
    "North": ["Delhi", "Punjab", "Haryana", "Uttarakhand"],
    "South": ["Karnataka", "Tamil Nadu", "Kerala", "Andhra Pradesh"],
    "East":  ["West Bengal", "Odisha", "Bihar", "Jharkhand"],
    "West":  ["Maharashtra", "Gujarat", "Rajasthan", "Goa"],
    "Central": ["Madhya Pradesh", "Chhattisgarh", "Uttar Pradesh"],
}

CITIES_BY_STATE = {
    "Delhi": ["New Delhi"], "Punjab": ["Ludhiana", "Amritsar"], "Haryana": ["Gurugram", "Faridabad"],
    "Uttarakhand": ["Dehradun"], "Karnataka": ["Bengaluru", "Mysuru"], "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Kerala": ["Kochi", "Thiruvananthapuram"], "Andhra Pradesh": ["Visakhapatnam", "Vijayawada"],
    "West Bengal": ["Kolkata", "Siliguri"], "Odisha": ["Bhubaneswar"], "Bihar": ["Patna"],
    "Jharkhand": ["Ranchi"], "Maharashtra": ["Mumbai", "Pune", "Nagpur"], "Gujarat": ["Ahmedabad", "Surat"],
    "Rajasthan": ["Jaipur", "Udaipur"], "Goa": ["Panaji"], "Madhya Pradesh": ["Indore", "Bhopal"],
    "Chhattisgarh": ["Raipur"], "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur"],
}

CATEGORIES = {
    "Electronics": {
        "products": [
            ("Laptop Pro 14", 78000, 58000), ("Laptop Air 13", 62000, 47000),
            ("Wireless Headphones", 4500, 2600), ("Smartwatch X2", 9500, 6200),
            ("4K Monitor 27in", 21000, 15500), ("Bluetooth Speaker", 3200, 1900),
            ("Mechanical Keyboard", 5200, 3300), ("Wireless Mouse", 1400, 750),
            ("Power Bank 20000mAh", 1800, 950), ("Tablet 10in", 26000, 19500),
        ],
        "seasonality_peak": [11, 12], "weekday_bias": 0.0, "popularity": 1.4,
    },
    "Home & Kitchen": {
        "products": [
            ("Air Fryer 4L", 6800, 4200), ("Mixer Grinder", 3400, 2100),
            ("Non-stick Cookware Set", 4200, 2600), ("Electric Kettle", 1500, 850),
            ("Vacuum Cleaner", 9800, 6900), ("Induction Cooktop", 2600, 1600),
            ("Water Purifier", 12500, 8700), ("Ceiling Fan Premium", 3100, 2000),
        ],
        "seasonality_peak": [10, 11], "weekday_bias": 0.1, "popularity": 1.1,
    },
    "Apparel": {
        "products": [
            ("Men's Casual Shirt", 1200, 650), ("Women's Kurti", 1400, 700),
            ("Denim Jeans", 1900, 1000), ("Running Shoes", 3400, 1900),
            ("Winter Jacket", 4800, 2700), ("Formal Blazer", 5200, 2900),
            ("Cotton T-Shirt Pack", 900, 420),
        ],
        "seasonality_peak": [10, 12, 1], "weekday_bias": 0.15, "popularity": 1.3,
    },
    "Sports & Fitness": {
        "products": [
            ("Yoga Mat Premium", 1100, 550), ("Adjustable Dumbbell Set", 6500, 4300),
            ("Treadmill Home", 42000, 31000), ("Cricket Bat Pro", 3200, 1800),
            ("Cycling Helmet", 1600, 850), ("Resistance Band Kit", 800, 380),
        ],
        "seasonality_peak": [1, 6], "weekday_bias": -0.05, "popularity": 0.9,
    },
    "Office Supplies": {
        "products": [
            ("Ergonomic Office Chair", 8900, 6100), ("Standing Desk", 15500, 11200),
            ("Notebook Pack (5)", 350, 150), ("Printer Ink Cartridge", 1200, 650),
            ("Desk Organizer", 650, 300), ("LED Desk Lamp", 1400, 750),
        ],
        "seasonality_peak": [6, 7], "weekday_bias": 0.25, "popularity": 0.8,
    },
}

SEGMENTS = {
    "High Value": {"share": 0.08, "order_freq_days": 14, "aov_mult": 2.6},
    "Loyal":      {"share": 0.22, "order_freq_days": 30, "aov_mult": 1.4},
    "Potential":  {"share": 0.30, "order_freq_days": 55, "aov_mult": 1.0},
    "At Risk":    {"share": 0.20, "order_freq_days": 95, "aov_mult": 0.8},
    "Inactive":   {"share": 0.20, "order_freq_days": 180, "aov_mult": 0.6},
}

FIRST_NAMES = ["Aarav","Vivaan","Aditya","Vihaan","Arjun","Sai","Reyansh","Ayaan","Krishna","Ishaan",
               "Ananya","Diya","Saanvi","Aadhya","Kiara","Myra","Pari","Anika","Navya","Riya",
               "Rohan","Karan","Neha","Priya","Rahul","Sanjay","Pooja","Meera","Vikram","Anjali"]
LAST_NAMES = ["Sharma","Verma","Patel","Reddy","Nair","Iyer","Gupta","Singh","Rao","Menon",
              "Kapoor","Joshi","Chatterjee","Mehta","Desai","Pillai","Bose","Kulkarni","Agarwal","Das"]

SALESPEOPLE = ["Ravi Kumar", "Anita Desai", "Suresh Iyer", "Priya Nair", "Manoj Rao",
               "Kavita Menon", "Deepak Sharma", "Sunita Verma"]

N_CUSTOMERS = 1400
N_PRODUCTS = sum(len(c["products"]) for c in CATEGORIES.values())

# ---------------------------------------------------------------------------
# Build customers
# ---------------------------------------------------------------------------
segment_names = list(SEGMENTS.keys())
segment_probs = [SEGMENTS[s]["share"] for s in segment_names]

customers = []
for cid in range(1, N_CUSTOMERS + 1):
    region = rng.choice(list(REGIONS.keys()), p=[0.24, 0.26, 0.16, 0.22, 0.12])
    state = rng.choice(STATES_BY_REGION[region])
    city = rng.choice(CITIES_BY_STATE[state])
    segment = rng.choice(segment_names, p=segment_probs)
    fname = rng.choice(FIRST_NAMES)
    lname = rng.choice(LAST_NAMES)
    customers.append({
        "customer_id": cid,
        "name": f"{fname} {lname}",
        "email": f"{fname.lower()}.{lname.lower()}{cid}@example.com",
        "city": city, "state": state, "region": region, "segment": segment,
        "signup_date": START_DATE + timedelta(days=int(rng.integers(0, 700))),
    })
customers_df = pd.DataFrame(customers)

# ---------------------------------------------------------------------------
# Build products
# ---------------------------------------------------------------------------
products = []
pid = 1
for cat, meta in CATEGORIES.items():
    for name, price, cost in meta["products"]:
        products.append({
            "product_id": pid, "product_name": name, "category": cat,
            "subcategory": cat, "price": price, "cost": cost,
            "popularity": meta["popularity"] * rng.uniform(0.7, 1.3),
            "seasonality_peak": meta["seasonality_peak"],
            "weekday_bias": meta["weekday_bias"],
        })
        pid += 1
products_df = pd.DataFrame(products)

# ---------------------------------------------------------------------------
# Simulate orders day by day
# ---------------------------------------------------------------------------
order_rows = []
order_id = 1

# Precompute customer "next order due" schedule
next_due = {}
for _, c in customers_df.iterrows():
    freq = SEGMENTS[c["segment"]]["order_freq_days"]
    next_due[c["customer_id"]] = c["signup_date"] + timedelta(days=int(rng.integers(0, freq)))

for date in ALL_DATES:
    year_idx = date.year - START_DATE.year
    month = date.month
    weekday = date.weekday()  # 0=Mon

    due_customers = customers_df[customers_df["customer_id"].map(
        lambda cid: next_due[cid] <= date and next_due[cid] >= date - timedelta(days=2)
    )]

    for _, cust in due_customers.iterrows():
        seg = SEGMENTS[cust["segment"]]
        region_meta = REGIONS[cust["region"]]

        # probability this customer actually orders today (not every "due" customer converts)
        if rng.random() > 0.55:
            # push due date forward a bit and skip
            next_due[cust["customer_id"]] = date + timedelta(days=int(rng.integers(3, seg["order_freq_days"])))
            continue

        # number of line items in this order
        n_items = rng.choice([1, 2, 3, 4], p=[0.45, 0.30, 0.17, 0.08])
        candidate_products = products_df.sample(
            n=min(n_items, len(products_df)),
            weights=products_df["popularity"], random_state=int(rng.integers(0, 1_000_000))
        )

        region_growth = (1 + region_meta["growth"]) ** year_idx
        month_season = 1.35 if month in (11, 12) else (0.85 if month in (5, 6) else 1.0)
        weekend_factor = 0.9 if weekday >= 5 else 1.0

        order_date = date
        region = cust["region"]
        salesperson = rng.choice(SALESPEOPLE)
        order_status = rng.choice(["Completed", "Completed", "Completed", "Completed", "Cancelled", "Returned"],
                                   p=[0.80, 0.0, 0.0, 0.0, 0.08, 0.12])

        for _, prod in candidate_products.iterrows():
            prod_month_boost = 1.25 if month in prod["seasonality_peak"] else 1.0
            weekday_adj = 1 + prod["weekday_bias"] if weekday < 5 else 1 - prod["weekday_bias"]

            base_qty = rng.choice([1, 1, 1, 2, 2, 3], p=[0.35, 0.2, 0.15, 0.15, 0.1, 0.05])
            qty = max(1, int(round(base_qty * region_meta["base_demand"] * month_season * prod_month_boost)))
            qty = min(qty, 6)

            discount = float(np.clip(rng.normal(0.06, 0.05), 0, 0.35))
            unit_price = prod["price"] * region_growth * weekday_adj * rng.uniform(0.97, 1.03)
            revenue = unit_price * qty * (1 - discount)
            cost_total = prod["cost"] * region_growth * qty
            profit = revenue - cost_total

            order_rows.append({
                "order_id": order_id, "order_date": order_date.strftime("%Y-%m-%d"),
                "customer_id": cust["customer_id"], "product_id": prod["product_id"],
                "region": region, "salesperson": salesperson, "order_status": order_status,
                "quantity": qty, "unit_price": round(unit_price, 2),
                "discount": round(discount, 3), "revenue": round(revenue, 2),
                "profit": round(profit, 2),
            })

        order_id += 1
        next_due[cust["customer_id"]] = date + timedelta(days=int(rng.integers(
            max(3, seg["order_freq_days"] // 2), seg["order_freq_days"] + 15)))

order_items_df = pd.DataFrame(order_rows)

# ---------------------------------------------------------------------------
# Inject a small number of realistic anomalies (revenue spikes/drops)
# ---------------------------------------------------------------------------
n_anomalies = max(30, int(len(order_items_df) * 0.004))
anomaly_idx = rng.choice(order_items_df.index, size=n_anomalies, replace=False)
for idx in anomaly_idx:
    direction = rng.choice(["spike", "drop"])
    if direction == "spike":
        mult = rng.uniform(4, 9)
    else:
        mult = rng.uniform(0.05, 0.2)
    order_items_df.loc[idx, "quantity"] = max(1, int(order_items_df.loc[idx, "quantity"] * mult))
    order_items_df.loc[idx, "revenue"] = round(order_items_df.loc[idx, "revenue"] * mult, 2)
    order_items_df.loc[idx, "profit"] = round(order_items_df.loc[idx, "profit"] * mult, 2)

# ---------------------------------------------------------------------------
# Merge into final flat CSV (one row per order line item, denormalized for convenience,
# but we also emit normalized tables for the relational DB seed).
# ---------------------------------------------------------------------------
order_items_df = order_items_df.merge(
    products_df[["product_id", "product_name", "category", "subcategory"]], on="product_id", how="left"
)
order_items_df = order_items_df.merge(
    customers_df[["customer_id", "name", "segment"]].rename(columns={"name": "customer_name"}),
    on="customer_id", how="left"
)

order_items_df["line_item_id"] = range(1, len(order_items_df) + 1)

final_cols = [
    "line_item_id", "order_id", "order_date", "customer_id", "customer_name", "segment",
    "region", "product_id", "product_name", "category", "subcategory", "salesperson",
    "order_status", "quantity", "unit_price", "discount", "revenue", "profit",
]
final_df = order_items_df[final_cols].sort_values(["order_date", "order_id"]).reset_index(drop=True)

final_df.to_csv("/home/claude/AI-Sales-Analytics/data/sample_sales.csv", index=False)
customers_df.to_csv("/home/claude/AI-Sales-Analytics/data/customers_seed.csv", index=False)
products_df.drop(columns=["seasonality_peak"]).to_csv("/home/claude/AI-Sales-Analytics/data/products_seed.csv", index=False)

print(f"Rows (line items): {len(final_df):,}")
print(f"Distinct orders:   {final_df['order_id'].nunique():,}")
print(f"Customers:         {customers_df.shape[0]:,}")
print(f"Products:          {products_df.shape[0]:,}")
print(f"Date range:        {final_df['order_date'].min()} -> {final_df['order_date'].max()}")
print(f"Total revenue:     {final_df['revenue'].sum():,.0f}")
