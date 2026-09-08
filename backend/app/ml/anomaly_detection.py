"""
Anomaly detection over order line items using Isolation Forest.

Features are chosen so anomalies reflect genuinely unusual *transactions*
rather than just "big orders from big customers":
    - revenue (line item)
    - quantity
    - unit_price
    - discount
    - revenue vs. that product's own historical median (ratio) -- this is
      what lets us flag "this order for Product X was 6x the usual size"
      rather than just "this is an expensive product".

Isolation Forest is trained on the whole filtered dataset (unsupervised --
no labels required, which is the correct approach here and easy to explain:
it isolates points that are easy to split off from the rest via random
partitioning, so consistently-unusual rows get shorter average path length
and thus a higher anomaly score).
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


FEATURES = ["revenue", "quantity", "unit_price", "discount", "revenue_vs_product_median"]


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.02) -> list:
    if df.empty or len(df) < 30:
        return []

    d = df.copy()
    product_median = d.groupby("product_id")["revenue"].transform("median").replace(0, np.nan)
    d["revenue_vs_product_median"] = (d["revenue"] / product_median).fillna(1.0)

    X = d[FEATURES].fillna(0)

    model = IsolationForest(
        n_estimators=200, contamination=contamination, random_state=42, n_jobs=-1
    )
    model.fit(X)
    raw_scores = model.decision_function(X)   # higher = more normal
    preds = model.predict(X)                  # -1 = anomaly, 1 = normal

    d["anomaly_score"] = (-raw_scores)  # flip so higher = more anomalous
    d["is_anomaly"] = preds == -1

    anomalies = d[d["is_anomaly"]].copy()
    if anomalies.empty:
        return []

    # Normalize scores to 0-100 for readability, then bucket into severity
    min_s, max_s = anomalies["anomaly_score"].min(), anomalies["anomaly_score"].max()
    span = (max_s - min_s) or 1.0
    anomalies["score_100"] = ((anomalies["anomaly_score"] - min_s) / span * 100).round(1)

    def severity(score):
        if score >= 70:
            return "High"
        elif score >= 35:
            return "Medium"
        return "Low"

    anomalies["severity"] = anomalies["score_100"].apply(severity)
    anomalies["expected_revenue"] = (anomalies["revenue"] / anomalies["revenue_vs_product_median"].replace(0, 1)).round(2)

    anomalies = anomalies.sort_values("score_100", ascending=False)

    out = anomalies[[
        "order_date", "product_name", "category", "region", "customer_name",
        "revenue", "expected_revenue", "quantity", "score_100", "severity",
    ]].head(200).copy()
    out["order_date"] = pd.to_datetime(out["order_date"]).dt.strftime("%Y-%m-%d")
    out = out.rename(columns={
        "order_date": "date", "revenue": "actual_value", "score_100": "anomaly_score",
    })
    return out.round(2).to_dict(orient="records")
