"""Customer opportunity analysis for the public portfolio demo."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def _safe_divide(
    numerator: pd.Series,
    denominator: pd.Series,
) -> pd.Series:
    """Divide numeric series while avoiding divide-by-zero errors."""

    denominator = pd.to_numeric(
        denominator,
        errors="coerce",
    ).replace(0, np.nan)

    numerator = pd.to_numeric(
        numerator,
        errors="coerce",
    )

    return numerator / denominator


def _customer_intervals(
    history: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate average and median days between purchases by customer."""

    interval_data = history[
        ["customer_id", "purchase_date"]
    ].copy()

    interval_data = interval_data.sort_values(
        ["customer_id", "purchase_date"]
    )

    interval_data["prior_purchase_date"] = (
        interval_data
        .groupby("customer_id")["purchase_date"]
        .shift(1)
    )

    interval_data["interval_days"] = (
        interval_data["purchase_date"]
        - interval_data["prior_purchase_date"]
    ).dt.days

    return (
        interval_data.groupby(
            "customer_id",
            as_index=False,
        )
        .agg(
            avg_purchase_interval_days=("interval_days", "mean"),
            median_purchase_interval_days=("interval_days", "median"),
        )
    )


def analyze_customers(
    history: pd.DataFrame,
    analysis_date: date = date(2026, 9, 9),
) -> pd.DataFrame:
    """Convert transaction history into explainable revenue-opportunity signals."""

    df = history.copy()

    required_columns = {
        "customer_id",
        "first_name",
        "last_name",
        "company_name",
        "store",
        "salesperson",
        "purchase_date",
        "product",
        "sale_value",
    }

    missing = required_columns.difference(df.columns)

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing))
        )

    df["purchase_date"] = pd.to_datetime(
        df["purchase_date"],
        errors="coerce",
    )

    df["sale_value"] = pd.to_numeric(
        df["sale_value"],
        errors="coerce",
    ).fillna(0.0)

    df = df.dropna(
        subset=[
            "customer_id",
            "purchase_date",
        ]
    ).copy()

    analysis_ts = pd.Timestamp(analysis_date)

    df = df[
        df["purchase_date"] <= analysis_ts
    ].copy()

    if df.empty:
        return pd.DataFrame()

    current_12_start = (
        analysis_ts
        - pd.DateOffset(months=12)
    )

    prior_12_start = (
        analysis_ts
        - pd.DateOffset(months=24)
    )

    customer = (
        df.groupby(
            "customer_id",
            as_index=False,
        )
        .agg(
            first_name=("first_name", "first"),
            last_name=("last_name", "first"),
            company_name=("company_name", "first"),
            store=("store", "last"),
            salesperson=("salesperson", "last"),
            first_purchase_date=("purchase_date", "min"),
            last_purchase_date=("purchase_date", "max"),
            purchase_count=("purchase_date", "size"),
            lifetime_revenue=("sale_value", "sum"),
            avg_purchase_value=("sale_value", "mean"),
            max_purchase_value=("sale_value", "max"),
            unique_products=("product", "nunique"),
        )
    )

    intervals = _customer_intervals(df)

    customer = customer.merge(
        intervals,
        on="customer_id",
        how="left",
    )

    current_12 = (
        df[
            df["purchase_date"].gt(current_12_start)
            & df["purchase_date"].le(analysis_ts)
        ]
        .groupby("customer_id")["sale_value"]
        .sum()
    )

    prior_12 = (
        df[
            df["purchase_date"].gt(prior_12_start)
            & df["purchase_date"].le(current_12_start)
        ]
        .groupby("customer_id")["sale_value"]
        .sum()
    )

    current_units = (
        df[
            df["purchase_date"].gt(current_12_start)
            & df["purchase_date"].le(analysis_ts)
        ]
        .groupby("customer_id")
        .size()
    )

    prior_units = (
        df[
            df["purchase_date"].gt(prior_12_start)
            & df["purchase_date"].le(current_12_start)
        ]
        .groupby("customer_id")
        .size()
    )

    customer["current_12m_revenue"] = (
        customer["customer_id"]
        .map(current_12)
        .fillna(0.0)
    )

    customer["prior_12m_revenue"] = (
        customer["customer_id"]
        .map(prior_12)
        .fillna(0.0)
    )

    customer["current_12m_purchases"] = (
        customer["customer_id"]
        .map(current_units)
        .fillna(0)
        .astype(int)
    )

    customer["prior_12m_purchases"] = (
        customer["customer_id"]
        .map(prior_units)
        .fillna(0)
        .astype(int)
    )

    customer["days_since_last_purchase"] = (
        analysis_ts
        - customer["last_purchase_date"]
    ).dt.days

    customer["revenue_change"] = (
        customer["current_12m_revenue"]
        - customer["prior_12m_revenue"]
    )

    customer["revenue_change_pct"] = _safe_divide(
        customer["revenue_change"],
        customer["prior_12m_revenue"],
    )

    customer["cycle_ratio"] = _safe_divide(
        customer["days_since_last_purchase"],
        customer["avg_purchase_interval_days"],
    )

    high_value_threshold = float(
        customer["lifetime_revenue"].quantile(0.75)
    )

    high_aov_threshold = float(
        customer["avg_purchase_value"].quantile(0.75)
    )

    customer["high_value_customer"] = (
        customer["lifetime_revenue"]
        >= high_value_threshold
    )

    customer["high_ticket_customer"] = (
        customer["avg_purchase_value"]
        >= high_aov_threshold
    )

    customer["revenue_decline_flag"] = (
        customer["prior_12m_revenue"].gt(0)
        & customer["current_12m_revenue"].lt(
            customer["prior_12m_revenue"] * 0.65
        )
    )

    customer["inactive_flag"] = (
        customer["days_since_last_purchase"]
        > 365
    )

    customer["dormant_flag"] = (
        customer["days_since_last_purchase"]
        > 540
    )

    customer["purchase_cycle_due"] = (
        customer["purchase_count"].ge(3)
        & customer["avg_purchase_interval_days"].between(
            180,
            900,
            inclusive="both",
        )
        & customer["cycle_ratio"].ge(0.90)
        & customer["cycle_ratio"].le(2.25)
    )

    customer["purchase_cycle_overdue"] = (
        customer["purchase_cycle_due"]
        & customer["cycle_ratio"].ge(1.10)
    )

    revenue_gap = (
        customer["prior_12m_revenue"]
        - customer["current_12m_revenue"]
    ).clip(lower=0)

    customer["reference_opportunity_value"] = np.where(
        customer["revenue_decline_flag"],
        np.maximum(
            revenue_gap,
            customer["avg_purchase_value"],
        ),
        customer["avg_purchase_value"],
    )

    customer[
        "reference_opportunity_value"
    ] = pd.to_numeric(
        customer["reference_opportunity_value"],
        errors="coerce",
    ).fillna(0.0)

    def classify(row: pd.Series) -> str:
        high_value = bool(
            row["high_value_customer"]
            or row["high_ticket_customer"]
        )

        if (
            row["purchase_cycle_due"]
            and row["revenue_decline_flag"]
            and high_value
        ):
            return "A-DUAL"

        if (
            row["purchase_cycle_due"]
            and high_value
        ):
            return "A-CYCLE"

        if (
            row["revenue_decline_flag"]
            and high_value
            and row["days_since_last_purchase"] <= 730
        ):
            return "A-DECLINE"

        if row["purchase_cycle_due"]:
            return "B-CYCLE"

        if row["revenue_decline_flag"]:
            return "B-DECLINE"

        if row["inactive_flag"]:
            return "B-INACTIVE"

        return "C-NURTURE"

    customer["priority_segment"] = (
        customer.apply(
            classify,
            axis=1,
        )
    )

    priority_order = {
        "A-DUAL": 1,
        "A-CYCLE": 2,
        "A-DECLINE": 3,
        "B-CYCLE": 4,
        "B-DECLINE": 5,
        "B-INACTIVE": 6,
        "C-NURTURE": 7,
    }

    customer["priority_rank"] = (
        customer["priority_segment"]
        .map(priority_order)
        .fillna(99)
        .astype(int)
    )

    def action_reason(row: pd.Series) -> str:
        if row["priority_segment"] == "A-DUAL":
            return (
                "High-value customer with both purchase-cycle "
                "and revenue-decline signals"
            )

        if row["priority_segment"] == "A-CYCLE":
            return (
                "High-value repeat customer appears due "
                "for another purchase"
            )

        if row["priority_segment"] == "A-DECLINE":
            return (
                "High-value customer shows material "
                "recent revenue decline"
            )

        if row["priority_segment"] == "B-CYCLE":
            return (
                "Repeat-purchase cadence suggests "
                "a follow-up opportunity"
            )

        if row["priority_segment"] == "B-DECLINE":
            return (
                "Recent revenue is materially below "
                "the prior 12-month period"
            )

        if row["priority_segment"] == "B-INACTIVE":
            return (
                "Customer has not purchased "
                "within the last 12 months"
            )

        return (
            "Maintain relationship and monitor "
            "for future purchase signals"
        )

    customer["action_reason"] = (
        customer.apply(
            action_reason,
            axis=1,
        )
    )

    customer["customer_name"] = (
        customer["first_name"].fillna("")
        + " "
        + customer["last_name"].fillna("")
    ).str.strip()

    customer["display_name"] = np.where(
        customer["company_name"]
        .fillna("")
        .str.strip()
        .ne(""),
        customer["company_name"],
        customer["customer_name"],
    )

    return (
        customer.sort_values(
            [
                "priority_rank",
                "reference_opportunity_value",
                "lifetime_revenue",
            ],
            ascending=[
                True,
                False,
                False,
            ],
        )
        .reset_index(drop=True)
    )


def build_action_queue(
    customer_analysis: pd.DataFrame,
    include_nurture: bool = False,
) -> pd.DataFrame:
    """Return the prioritized sales-action queue."""

    if customer_analysis.empty:
        return customer_analysis.copy()

    queue = customer_analysis.copy()

    if not include_nurture:
        queue = queue[
            queue["priority_segment"]
            != "C-NURTURE"
        ].copy()

    return (
        queue.sort_values(
            [
                "priority_rank",
                "reference_opportunity_value",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .reset_index(drop=True)
    )


def segment_summary(
    customer_analysis: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize customer opportunity segments."""

    if customer_analysis.empty:
        return pd.DataFrame(
            columns=[
                "priority_segment",
                "customers",
                "lifetime_revenue",
                "reference_opportunity_value",
            ]
        )

    return (
        customer_analysis.groupby(
            [
                "priority_rank",
                "priority_segment",
            ],
            as_index=False,
        )
        .agg(
            customers=("customer_id", "nunique"),
            lifetime_revenue=("lifetime_revenue", "sum"),
            reference_opportunity_value=(
                "reference_opportunity_value",
                "sum",
            ),
        )
        .sort_values("priority_rank")
        .drop(columns=["priority_rank"])
        .reset_index(drop=True)
    )
