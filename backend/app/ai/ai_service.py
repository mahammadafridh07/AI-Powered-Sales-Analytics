"""
AI Sales Analyst service.

Architecture:

    User Question
        -> Question Understanding
        -> Analytics Intent
        -> Safe Analytics Query
        -> Execute Read-Only Analytics
        -> Return Structured Result
        -> Optional LLM Explanation
        -> Business Recommendation

When LLM_API_KEY is not configured, the service still works using
deterministic, data-grounded template answers.
"""

import json
import re
from datetime import timedelta
from typing import Optional

import httpx
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.analytics import engine as A


# ---------------------------------------------------------------------------
# Intent detection
# ---------------------------------------------------------------------------

INTENT_PATTERNS = [
    ("top_product", r"\b(best|top|highest).*(product|item|sell)"),
    ("worst_product", r"\b(worst|lowest|underperform).*(product|item)"),
    ("region_revenue", r"\bregion\b.*(highest|top|best|revenue|perform)"),
    (
        "region_growth",
        r"\b(growing|growth|fastest)\b.*region|region.*\bgrow",
    ),
    ("category_revenue", r"\bcategory|categories\b"),
    (
        "customer_at_risk",
        r"\bat.?risk\b.*customer|customer.*\bat.?risk\b",
    ),
    ("total_revenue", r"\b(total|overall)\b.*(revenue|sales)"),
    (
        "summary",
        r"\bsummary|overview|how (are|is) (we|business|sales) doing\b",
    ),
    (
        "forecast",
        r"\bforecast|predict|next (month|week|quarter)|expected revenue\b",
    ),
    ("risk", r"\brisk|declin|drop|down\b"),
    ("recommend", r"\brecommend|promote|should we\b"),
]


def _detect_intent(question: str) -> str:
    """Detect a supported analytics intent from the user's question."""
    q = question.lower()

    for intent, pattern in INTENT_PATTERNS:
        if re.search(pattern, q):
            return intent

    return "summary"


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def _gather_data(db: Session, intent: str) -> dict:
    """
    Execute the appropriate SAFE analytics query for the detected intent.

    No raw SQL is generated from the user's question.
    """
    df = A.load_dataframe(db)

    if df.empty:
        return {
            "intent": intent,
            "data": None,
            "note": "No sales data has been uploaded yet.",
        }

    max_date = df["order_date"].max()

    last_30 = df[
        df["order_date"] > max_date - timedelta(days=30)
    ]

    prev_30 = df[
        (df["order_date"] > max_date - timedelta(days=60))
        & (df["order_date"] <= max_date - timedelta(days=30))
    ]

    if intent == "top_product":
        data = A.top_products(df, n=5)

    elif intent == "worst_product":
        data = A.top_products(df, n=5, ascending=True)

    elif intent == "region_revenue":
        data = A.revenue_by_region(df)

    elif intent == "region_growth":
        data = A.growth_by_region(df)

    elif intent == "category_revenue":
        data = A.revenue_by_category(df)

    elif intent == "customer_at_risk":
        seg = df[df["segment"] == "At Risk"]
        data = A.top_customers(seg, n=10)

    elif intent == "total_revenue":
        data = A.kpi_summary(last_30, prev_30)

    elif intent == "risk":
        data = {
            "declining_categories": [
                c for c in A.revenue_by_category(last_30)
            ],
            "growth_by_region": A.growth_by_region(df),
        }

    elif intent == "recommend":
        data = {
            "top_products": A.top_products(df, n=5),
            "worst_products": A.top_products(
                df,
                n=5,
                ascending=True,
            ),
            "growth_by_region": A.growth_by_region(df),
        }

    else:
        # Summary / forecast fallback.
        data = {
            "kpis": A.kpi_summary(last_30, prev_30),
            "top_products": A.top_products(df, n=5),
            "revenue_by_region": A.revenue_by_region(df),
            "revenue_by_category": A.revenue_by_category(df),
        }

    return {
        "intent": intent,
        "data": data,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt_currency(value) -> str:
    """Format Indian currency values in a readable form."""
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0.0

    if value >= 10_000_000:
        return f"₹{value / 10_000_000:.2f} Cr"

    if value >= 100_000:
        return f"₹{value / 100_000:.2f} L"

    return f"₹{value:,.0f}"


# ---------------------------------------------------------------------------
# Template-based fallback answer
# ---------------------------------------------------------------------------

def _template_answer(intent: str, payload: dict) -> str:
    """
    Natural, deterministic, data-grounded answer used when no LLM
    key is configured.
    """
    data = payload.get("data")

    if data is None:
        return payload.get(
            "note",
            "No sales data is available yet. "
            "Upload a sales file to get started.",
        )

    # -----------------------------------------------------------------------
    # Product performance
    # -----------------------------------------------------------------------
    if intent in ("top_product", "worst_product") and data:
        product = data[0]

        if intent == "top_product":
            label = "The top-performing product"
        else:
            label = "The lowest-performing product"

        return (
            f"{label} by revenue is "
            f"{product['product_name']} "
            f"from {product['category']}, generating "
            f"{_fmt_currency(product['revenue'])} in revenue "
            f"from {product['units_sold']:,.0f} units sold."
        )

    # -----------------------------------------------------------------------
    # Region / category revenue
    # -----------------------------------------------------------------------
    if intent in ("region_revenue", "category_revenue") and data:
        key = "region" if intent == "region_revenue" else "category"

        first = data[0]

        label = "region" if key == "region" else "category"

        return (
            f"{first[key]} generated the highest revenue at "
            f"{_fmt_currency(first['revenue'])}, with "
            f"{_fmt_currency(first['profit'])} in profit. "
            f"It is currently the strongest-performing "
            f"{label} in the dataset."
        )

    # -----------------------------------------------------------------------
    # Region growth
    # -----------------------------------------------------------------------
    if intent == "region_growth" and data:
        first = data[0]

        if first["growth_pct"] >= 0:
            direction = "grew"
        else:
            direction = "declined"

        return (
            f"{first['region']} is the fastest-growing region, "
            f"having {direction} "
            f"{abs(first['growth_pct']):.1f}% over the last "
            f"30 days compared with the previous 30-day period. "
            f"Its recent revenue was "
            f"{_fmt_currency(first['recent_30d_revenue'])}."
        )

    # -----------------------------------------------------------------------
    # Revenue KPI
    # -----------------------------------------------------------------------
    if intent == "total_revenue" and isinstance(data, dict):
        rev = data.get("revenue", {})

        value = rev.get("value", 0)
        growth = rev.get("growth_pct", 0)

        if growth >= 0:
            direction = "increased"
        else:
            direction = "decreased"

        return (
            f"Revenue for the last 30 days was "
            f"{_fmt_currency(value)}, which {direction} by "
            f"{abs(growth):.1f}% compared with the previous "
            f"30-day period."
        )

    # -----------------------------------------------------------------------
    # Customers at risk
    # -----------------------------------------------------------------------
    if intent == "customer_at_risk" and data:
        top_customer = data[0]

        return (
            "There are customers currently classified as "
            "'At Risk'. The highest-value at-risk customer is "
            f"{top_customer['customer_name']}, with lifetime revenue "
            f"of {_fmt_currency(top_customer['revenue'])} across "
            f"{top_customer['orders']} orders. "
            "A targeted win-back campaign could help improve retention."
        )

    # -----------------------------------------------------------------------
    # Risk analysis
    # -----------------------------------------------------------------------
    if intent == "risk" and isinstance(data, dict):
        growth = data.get("growth_by_region", [])

        if growth:
            strongest = growth[0]
            weakest = growth[-1]

            return (
                f"From a regional perspective, "
                f"{strongest['region']} is showing the strongest "
                f"growth at {strongest['growth_pct']:+.1f}%, while "
                f"{weakest['region']} is the weakest performer at "
                f"{weakest['growth_pct']:+.1f}%. "
                "These regions are useful candidates for targeted "
                "business review."
            )

    # -----------------------------------------------------------------------
    # Recommendations
    # -----------------------------------------------------------------------
    if intent == "recommend" and isinstance(data, dict):
        top_products = data.get("top_products", [])
        growth = data.get("growth_by_region", [])

        parts = []

        if top_products:
            parts.append(
                f"{top_products[0]['product_name']} is currently the "
                "strongest product by revenue at "
                f"{_fmt_currency(top_products[0]['revenue'])}."
            )

        if growth:
            parts.append(
                f"{growth[0]['region']} is the fastest-growing region "
                f"at {growth[0]['growth_pct']:+.1f}%."
            )

        if parts:
            return (
                "Based on the available sales analytics, "
                + " ".join(parts)
                + " Consider prioritizing these areas in marketing "
                "and sales planning."
            )

    # -----------------------------------------------------------------------
    # Summary / forecast fallback
    # -----------------------------------------------------------------------
    if intent in ("summary", "forecast") and isinstance(data, dict):
        kpis = data.get("kpis", {})

        revenue = kpis.get("revenue", {})
        profit = kpis.get("profit", {})

        if revenue or profit:
            revenue_value = revenue.get("value", 0)
            profit_value = profit.get("value", 0)

            return (
                "The latest sales data shows revenue of "
                f"{_fmt_currency(revenue_value)} and profit of "
                f"{_fmt_currency(profit_value)} over the recent "
                "period. The detailed dashboard provides the "
                "supporting product, regional, and category "
                "breakdowns."
            )

    # -----------------------------------------------------------------------
    # Final safe fallback
    # -----------------------------------------------------------------------
    return (
        "I analyzed the available sales data successfully. "
        "The detailed results are available in the dashboard, "
        "including revenue, profit, product, customer, and "
        "regional performance."
    )


# ---------------------------------------------------------------------------
# Optional LLM explanation
# ---------------------------------------------------------------------------

async def _call_llm(
    question: str,
    intent: str,
    data: dict,
) -> Optional[str]:
    """
    Call the configured LLM provider using only structured analytics data.

    Returns None on any failure so the application can safely fall back
    to the deterministic template answer.
    """
    if not settings.ai_configured:
        return None

    system_prompt = (
        "You are an AI Sales Analyst embedded in a business analytics "
        "dashboard. You are given a user's question and a JSON payload "
        "of pre-computed, verified analytics results. These numbers are "
        "already correct. Do not recompute or guess numbers. Answer "
        "conversationally in 2-5 sentences, reference concrete numbers "
        "from the payload, and end with one short, clearly labeled "
        "business recommendation. Do not invent data that is not "
        "present in the payload."
    )

    user_content = (
        f"Question: {question}\n\n"
        f"Analytics payload (intent={intent}):\n"
        f"{json.dumps(data, default=str)[:6000]}"
    )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.LLM_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.LLM_MODEL,
                    "max_tokens": 500,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_content,
                        }
                    ],
                },
            )

            response.raise_for_status()

            body = response.json()

            text_blocks = [
                block["text"]
                for block in body.get("content", [])
                if block.get("type") == "text"
            ]

            return "\n".join(text_blocks).strip() or None

    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main AI question handler
# ---------------------------------------------------------------------------

async def answer_question(
    db: Session,
    question: str,
) -> dict:
    """
    Process a user question and return a safe, data-grounded answer.
    """
    intent = _detect_intent(question)

    payload = _gather_data(db, intent)

    llm_answer = await _call_llm(
        question,
        intent,
        payload.get("data"),
    )

    if llm_answer:
        answer = llm_answer
    else:
        answer = _template_answer(
            intent,
            payload,
        )

    return {
        "answer": answer,
        "data": payload.get("data"),
        "ai_configured": settings.ai_configured,
    }


# ---------------------------------------------------------------------------
# Dashboard business insights
# ---------------------------------------------------------------------------

async def generate_insights(db: Session) -> list:
    """
    Generate rule-based, data-driven dashboard insights.

    Works fully without an LLM key.
    """
    df = A.load_dataframe(db)

    if df.empty:
        return []

    max_date = df["order_date"].max()

    last_30 = df[
        df["order_date"] > max_date - timedelta(days=30)
    ]

    prev_30 = df[
        (df["order_date"] > max_date - timedelta(days=60))
        & (df["order_date"] <= max_date - timedelta(days=30))
    ]

    insights = []

    # -----------------------------------------------------------------------
    # Category changes
    # -----------------------------------------------------------------------
    cat_recent = (
        last_30.groupby("category")["revenue"]
        .sum()
    )

    cat_prev = (
        prev_30.groupby("category")["revenue"]
        .sum()
    )

    for category in cat_recent.index:
        prev_value = cat_prev.get(category, 0)
        recent_value = cat_recent.get(category, 0)

        if prev_value == 0:
            continue

        change = (
            (recent_value - prev_value)
            / prev_value
            * 100
        )

        if change >= 12:
            insights.append(
                {
                    "type": "opportunity",
                    "icon": "trending-up",
                    "title": "Revenue Opportunity",
                    "text": (
                        f"{category} revenue increased "
                        f"{change:.0f}% over the last 30 days."
                    ),
                }
            )

        elif change <= -12:
            insights.append(
                {
                    "type": "risk",
                    "icon": "trending-down",
                    "title": "Risk",
                    "text": (
                        f"{category} revenue declined "
                        f"{abs(change):.0f}% over the last 30 days."
                    ),
                }
            )

    # -----------------------------------------------------------------------
    # At-risk customers
    # -----------------------------------------------------------------------
    at_risk = (
        df[df["segment"] == "At Risk"]["customer_id"]
        .nunique()
    )

    if at_risk > 0:
        insights.append(
            {
                "type": "retention",
                "icon": "alert-triangle",
                "title": "Customer Retention",
                "text": (
                    f"{at_risk} customers are currently classified "
                    "as 'At Risk'. Consider a targeted win-back campaign."
                ),
            }
        )

    # -----------------------------------------------------------------------
    # Regional growth
    # -----------------------------------------------------------------------
    growth = A.growth_by_region(df)

    if growth:
        best = growth[0]

        if best["growth_pct"] > 5:
            insights.append(
                {
                    "type": "opportunity",
                    "icon": "map-pin",
                    "title": "Regional Strategy",
                    "text": (
                        f"{best['region']} is growing fastest at "
                        f"{best['growth_pct']:.1f}% "
                        "(30-day vs prior 30-day revenue)."
                    ),
                }
            )

    return insights[:8]