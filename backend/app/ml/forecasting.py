"""
Sales forecasting.

Approach:
1. Aggregate order-level sales into a continuous daily revenue time series.
2. Engineer lag, rolling, calendar, trend, and seasonality features.
3. Use a time-based validation split on the last 20% of observations.
4. Compare:
      - Seasonal Naive baseline
      - Random Forest Regressor
      - XGBoost Regressor
5. Train tree models on log1p(revenue) to reduce the effect of extreme spikes.
6. Select the model with the lowest validation MAPE.
7. Refit the winning model on all available data.
8. Forecast the requested horizon recursively.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_21",
    "lag_28",
    "rolling_mean_7",
    "rolling_mean_14",
    "rolling_mean_28",
    "rolling_std_7",
    "rolling_std_14",
    "day_of_week",
    "day_of_month",
    "week_of_year",
    "month",
    "quarter",
    "time_index",
]


# ---------------------------------------------------------------------------
# Result object
# ---------------------------------------------------------------------------

@dataclass
class ForecastResult:
    model_name: str
    metrics: dict
    history: list
    forecast: list


# ---------------------------------------------------------------------------
# Daily time series
# ---------------------------------------------------------------------------

def _build_daily_series(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales to daily revenue and fill missing calendar days."""

    daily = (
        df.set_index("order_date")
        .resample("D")["revenue"]
        .sum()
        .reset_index()
    )

    daily.columns = ["date", "revenue"]

    if daily.empty:
        return daily

    full_range = pd.date_range(
        start=daily["date"].min(),
        end=daily["date"].max(),
        freq="D",
    )

    daily = (
        daily.set_index("date")
        .reindex(full_range, fill_value=0)
        .rename_axis("date")
        .reset_index()
    )

    return daily


# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------

def _engineer_features(daily: pd.DataFrame) -> pd.DataFrame:
    """
    Create explainable lag, rolling, calendar and trend features.

    All rolling features are shifted by one day so that the current day's
    revenue is never used to construct its own predictors.
    """

    d = daily.copy()

    # Lag features
    d["lag_1"] = d["revenue"].shift(1)
    d["lag_7"] = d["revenue"].shift(7)
    d["lag_14"] = d["revenue"].shift(14)
    d["lag_21"] = d["revenue"].shift(21)
    d["lag_28"] = d["revenue"].shift(28)

    # Rolling statistics using only historical values
    shifted = d["revenue"].shift(1)

    d["rolling_mean_7"] = shifted.rolling(7).mean()
    d["rolling_mean_14"] = shifted.rolling(14).mean()
    d["rolling_mean_28"] = shifted.rolling(28).mean()

    d["rolling_std_7"] = shifted.rolling(7).std()
    d["rolling_std_14"] = shifted.rolling(14).std()

    # Calendar features
    d["day_of_week"] = d["date"].dt.dayofweek
    d["day_of_month"] = d["date"].dt.day
    d["week_of_year"] = d["date"].dt.isocalendar().week.astype(int)
    d["month"] = d["date"].dt.month
    d["quarter"] = d["date"].dt.quarter

    # Long-term time index
    d["time_index"] = np.arange(len(d))

    return d


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _mape(y_true, y_pred) -> float:
    """
    Mean Absolute Percentage Error.

    Zero actual values are excluded because percentage error is undefined
    when the actual value is zero.
    """

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mask = y_true != 0

    if mask.sum() == 0:
        return 0.0

    return float(
        np.mean(
            np.abs(
                (y_true[mask] - y_pred[mask])
                / y_true[mask]
            )
        )
        * 100
    )


def _score(y_true, y_pred) -> dict:
    """Calculate MAE, RMSE and MAPE."""

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    return {
        "mae": round(
            float(mean_absolute_error(y_true, y_pred)),
            2,
        ),
        "rmse": round(
            float(np.sqrt(mean_squared_error(y_true, y_pred))),
            2,
        ),
        "mape": round(
            _mape(y_true, y_pred),
            2,
        ),
    }


# ---------------------------------------------------------------------------
# Model builders
# ---------------------------------------------------------------------------

def _build_random_forest() -> RandomForestRegressor:
    """Create the Random Forest model."""

    return RandomForestRegressor(
        n_estimators=500,
        max_depth=10,
        min_samples_leaf=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
    )


def _build_xgboost() -> XGBRegressor:
    """Create the XGBoost model."""

    return XGBRegressor(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        min_child_weight=3,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.05,
        reg_lambda=1.0,
        random_state=42,
        objective="reg:squarederror",
        verbosity=0,
    )


# ---------------------------------------------------------------------------
# Seasonal baseline
# ---------------------------------------------------------------------------

def _seasonal_naive_prediction(
    history: pd.Series,
    date: pd.Timestamp,
) -> float:
    """
    Forecast using the average of the same weekday from the previous
    four weeks.
    """

    values = []

    for weeks_back in range(1, 5):
        target_date = date - pd.Timedelta(days=7 * weeks_back)

        if target_date in history.index:
            values.append(float(history.loc[target_date]))

    if values:
        return float(np.mean(values))

    if len(history) > 0:
        return float(history.iloc[-1])

    return 0.0


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

def run_forecast(
    df: pd.DataFrame,
    horizon_days: int = 30,
) -> Optional[ForecastResult]:

    if df.empty:
        return None

    # -----------------------------------------------------------------------
    # Build daily time series
    # -----------------------------------------------------------------------

    daily = _build_daily_series(df)

    if daily.empty:
        return None

    # -----------------------------------------------------------------------
    # Engineer features
    # -----------------------------------------------------------------------

    feat = (
        _engineer_features(daily)
        .dropna()
        .reset_index(drop=True)
    )

    # Need enough historical data for the 28-day lag + validation.
    if len(feat) < 60:
        return None

    # -----------------------------------------------------------------------
    # Time-based train / validation split
    # -----------------------------------------------------------------------

    split_idx = int(len(feat) * 0.8)

    train = feat.iloc[:split_idx].copy()
    valid = feat.iloc[split_idx:].copy()

    if train.empty or valid.empty:
        return None

    X_train = train[FEATURE_COLS]
    y_train = train["revenue"]

    X_valid = valid[FEATURE_COLS]
    y_valid = valid["revenue"]

    # -----------------------------------------------------------------------
    # Seasonal Naive baseline
    # -----------------------------------------------------------------------

    history_for_baseline = (
        daily.set_index("date")["revenue"]
        .copy()
    )

    baseline_predictions = []

    for date in valid["date"]:
        pred = _seasonal_naive_prediction(
            history_for_baseline,
            date,
        )
        baseline_predictions.append(pred)

    baseline_predictions = np.asarray(
        baseline_predictions,
        dtype=float,
    )

    baseline_metrics = _score(
        y_valid,
        baseline_predictions,
    )

    # -----------------------------------------------------------------------
    # Random Forest
    #
    # Train on log1p(revenue) to reduce the influence of unusually large
    # revenue spikes.
    # -----------------------------------------------------------------------

    rf = _build_random_forest()

    rf.fit(
        X_train,
        np.log1p(y_train),
    )

    rf_valid_log = rf.predict(X_valid)

    rf_pred = np.maximum(
        0.0,
        np.expm1(rf_valid_log),
    )

    rf_metrics = _score(
        y_valid,
        rf_pred,
    )

    # -----------------------------------------------------------------------
    # XGBoost
    # -----------------------------------------------------------------------

    xgb = _build_xgboost()

    xgb.fit(
        X_train,
        np.log1p(y_train),
    )

    xgb_valid_log = xgb.predict(X_valid)

    xgb_pred = np.maximum(
        0.0,
        np.expm1(xgb_valid_log),
    )

    xgb_metrics = _score(
        y_valid,
        xgb_pred,
    )

    # -----------------------------------------------------------------------
    # Model comparison
    # -----------------------------------------------------------------------

    metrics = {
        "Baseline (Seasonal Naive)": baseline_metrics,
        "Random Forest": rf_metrics,
        "XGBoost": xgb_metrics,
    }

    # Pick the model with the lowest validation MAPE.
    best_name = min(
        metrics,
        key=lambda name: metrics[name]["mape"],
    )

    # -----------------------------------------------------------------------
    # Refit winning model on all available feature data
    # -----------------------------------------------------------------------

    model_map = {
        "Random Forest": rf,
        "XGBoost": xgb,
    }

    full_X = feat[FEATURE_COLS]
    full_y = feat["revenue"]

    if best_name == "Random Forest":
        final_model = _build_random_forest()

        final_model.fit(
            full_X,
            np.log1p(full_y),
        )

    elif best_name == "XGBoost":
        final_model = _build_xgboost()

        final_model.fit(
            full_X,
            np.log1p(full_y),
        )

    else:
        final_model = None

    # -----------------------------------------------------------------------
    # Residual uncertainty
    # -----------------------------------------------------------------------

    if best_name == "Random Forest":
        validation_residuals = y_valid.values - rf_pred

    elif best_name == "XGBoost":
        validation_residuals = y_valid.values - xgb_pred

    else:
        validation_residuals = (
            y_valid.values - baseline_predictions
        )

    residual_std = float(
        np.std(validation_residuals)
    )

    # -----------------------------------------------------------------------
    # Recursive future forecasting
    # -----------------------------------------------------------------------

    working = (
        daily.set_index("date")["revenue"]
        .astype(float)
        .copy()
    )

    last_date = working.index.max()

    forecast_rows = []

    for i in range(1, horizon_days + 1):

        next_date = last_date + pd.Timedelta(days=i)

        # Historical values available before next_date.
        lag_1 = (
            working.iloc[-1]
            if len(working) >= 1
            else 0.0
        )

        lag_7 = (
            working.iloc[-7]
            if len(working) >= 7
            else working.mean()
        )

        lag_14 = (
            working.iloc[-14]
            if len(working) >= 14
            else working.mean()
        )

        lag_21 = (
            working.iloc[-21]
            if len(working) >= 21
            else working.mean()
        )

        lag_28 = (
            working.iloc[-28]
            if len(working) >= 28
            else working.mean()
        )

        rolling_mean_7 = (
            working.iloc[-7:].mean()
            if len(working) >= 7
            else working.mean()
        )

        rolling_mean_14 = (
            working.iloc[-14:].mean()
            if len(working) >= 14
            else working.mean()
        )

        rolling_mean_28 = (
            working.iloc[-28:].mean()
            if len(working) >= 28
            else working.mean()
        )

        rolling_std_7 = (
            working.iloc[-7:].std()
            if len(working) >= 7
            else 0.0
        )

        rolling_std_14 = (
            working.iloc[-14:].std()
            if len(working) >= 14
            else 0.0
        )

        if pd.isna(rolling_std_7):
            rolling_std_7 = 0.0

        if pd.isna(rolling_std_14):
            rolling_std_14 = 0.0

        # ---------------------------------------------------------------
        # Baseline forecast
        # ---------------------------------------------------------------

        if best_name == "Baseline (Seasonal Naive)":

            pred = _seasonal_naive_prediction(
                working,
                next_date,
            )

        # ---------------------------------------------------------------
        # ML forecast
        # ---------------------------------------------------------------

        else:

            row = pd.DataFrame(
                [
                    {
                        "lag_1": lag_1,
                        "lag_7": lag_7,
                        "lag_14": lag_14,
                        "lag_21": lag_21,
                        "lag_28": lag_28,
                        "rolling_mean_7": rolling_mean_7,
                        "rolling_mean_14": rolling_mean_14,
                        "rolling_mean_28": rolling_mean_28,
                        "rolling_std_7": rolling_std_7,
                        "rolling_std_14": rolling_std_14,
                        "day_of_week": next_date.dayofweek,
                        "day_of_month": next_date.day,
                        "week_of_year": int(next_date.isocalendar().week),
                        "month": next_date.month,
                        "quarter": next_date.quarter,
                        "time_index": len(daily) + i,
                    }
                ]
            )

            pred_log = final_model.predict(
                row[FEATURE_COLS]
            )[0]

            pred = float(
                np.maximum(
                    0.0,
                    np.expm1(pred_log),
                )
            )

        pred = max(
            0.0,
            float(pred),
        )

        # Add predicted value to working history so the next forecast
        # day can use it as a lag.
        working.loc[next_date] = pred

        lower = max(
            0.0,
            pred - 1.28 * residual_std,
        )

        upper = (
            pred + 1.28 * residual_std
        )

        forecast_rows.append(
            {
                "date": next_date.strftime("%Y-%m-%d"),
                "revenue": round(pred, 2),
                "lower": round(lower, 2),
                "upper": round(upper, 2),
            }
        )

    # -----------------------------------------------------------------------
    # Historical rows for the frontend chart
    # -----------------------------------------------------------------------

    history_rows = [
        {
            "date": date.strftime("%Y-%m-%d"),
            "revenue": round(float(value), 2),
        }
        for date, value in working.iloc[:-horizon_days]
        .tail(120)
        .items()
    ]

    # -----------------------------------------------------------------------
    # Return
    # -----------------------------------------------------------------------

    return ForecastResult(
        model_name=best_name,
        metrics=metrics,
        history=history_rows,
        forecast=forecast_rows,
    )