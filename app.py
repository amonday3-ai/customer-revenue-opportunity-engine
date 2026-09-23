from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from engine import (
    analyze_customers,
    build_action_queue,
    build_demo_customer_history,
    segment_summary,
)


st.set_page_config(
    page_title="Customer Revenue Opportunity Engine",
    page_icon="🎯",
    layout="wide",
)

ANALYSIS_DATE = date(2026, 9, 9)


def money(value: float) -> str:
    return f"${value:,.0f}"


st.title("🎯 Customer Revenue Opportunity Engine")

st.markdown(
    """
    **Customer lifecycle intelligence for prioritizing sales outreach**

    This public portfolio demo converts multi-year customer purchase history
    into an explainable action queue using recency, revenue decline,
    purchase cadence, and customer value signals.
    """
)

st.caption(
    "Portfolio edition • 100% synthetic data • No employer, customer, contact, "
    "pricing, or proprietary sales records are included."
)

with st.sidebar:
    st.header("Opportunity Controls")

    priority_filter = st.multiselect(
        "Priority segments",
        options=[
            "A-DUAL",
            "A-CYCLE",
            "A-DECLINE",
            "B-CYCLE",
            "B-DECLINE",
            "B-INACTIVE",
            "C-NURTURE",
        ],
        default=[
            "A-DUAL",
            "A-CYCLE",
            "A-DECLINE",
            "B-CYCLE",
            "B-DECLINE",
            "B-INACTIVE",
        ],
    )

    st.divider()
    st.subheader("Signal Design")
    st.markdown(
        """
        **Primary signals**
        - Recency
        - Purchase frequency
        - Lifetime value
        - Recent revenue decline
        - Repeat-purchase cadence
        - Inactivity / dormancy

        **Priority logic**
        - A = highest review priority
        - B = actionable opportunity
        - C = nurture / monitor
        """
    )

    st.warning(
        "Opportunity values are prioritization references, not guaranteed "
        "future revenue or recoverable sales."
    )

history = build_demo_customer_history(
    analysis_date=ANALYSIS_DATE,
)

customers = analyze_customers(
    history,
    analysis_date=ANALYSIS_DATE,
)

queue = build_action_queue(
    customers,
    include_nurture=True,
)

summary = segment_summary(
    customers
)

total_customers = int(
    customers["customer_id"].nunique()
)

actionable = customers[
    customers["priority_segment"] != "C-NURTURE"
].copy()

priority_a = customers[
    customers["priority_segment"].str.startswith("A-")
].copy()

cycle_opportunities = customers[
    customers["purchase_cycle_due"]
].copy()

decline_opportunities = customers[
    customers["revenue_decline_flag"]
].copy()

dormant_customers = customers[
    customers["dormant_flag"]
].copy()

reference_value = float(
    actionable["reference_opportunity_value"].sum()
)

with st.expander(
    "💼 Business Problem & Approach",
    expanded=False,
):
    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            ### Business problem

            Customer transaction history can become a giant list with little
            guidance about where sales teams should focus first.

            Management needs to know:

            - Which customers deserve immediate review?
            - Which high-value accounts have gone quiet?
            - Which customers show material revenue decline?
            - Which repeat buyers appear due for another purchase?
            - How can outreach be prioritized consistently?
            """
        )

    with right:
        st.markdown(
            """
            ### Analytical approach

            1. Aggregate transaction history to the customer level.
            2. Measure recency, frequency, and lifetime value.
            3. Compare recent 12-month revenue with the prior 12 months.
            4. Estimate historical purchase cadence.
            5. Detect cycle-due and inactivity signals.
            6. Apply transparent A/B/C prioritization logic.
            7. Produce a management-ready sales action queue.
            """
        )

st.subheader("Executive Opportunity Snapshot")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Customers Analyzed",
    f"{total_customers:,}",
)

k2.metric(
    "Actionable A + B Customers",
    f"{len(actionable):,}",
)

k3.metric(
    "Priority A Customers",
    f"{len(priority_a):,}",
)

k4.metric(
    "Reference Opportunity Value",
    money(reference_value),
)

k5, k6, k7 = st.columns(3)

k5.metric(
    "Purchase-Cycle Signals",
    f"{len(cycle_opportunities):,}",
)

k6.metric(
    "Revenue-Decline Signals",
    f"{len(decline_opportunities):,}",
)

k7.metric(
    "Dormant Customers",
    f"{len(dormant_customers):,}",
)

st.info(
    "The queue prioritizes customer review using observed historical behavior. "
    "A higher priority is a sales-action signal, not a prediction that the "
    "customer will purchase again."
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Action Queue",
        "Opportunity Segments",
        "Sales Rep & Store Views",
        "Customer Signals",
    ]
)

with tab1:
    st.subheader("Prioritized Sales Action Queue")

    filtered_queue = queue[
        queue["priority_segment"].isin(
            priority_filter
        )
    ].copy()

    display_queue = filtered_queue[
        [
            "display_name",
            "priority_segment",
            "store",
            "salesperson",
            "days_since_last_purchase",
            "purchase_count",
            "lifetime_revenue",
            "current_12m_revenue",
            "prior_12m_revenue",
            "reference_opportunity_value",
            "action_reason",
        ]
    ].rename(
        columns={
            "display_name": "Customer",
            "priority_segment": "Priority",
            "store": "Store",
            "salesperson": "Sales Rep",
            "days_since_last_purchase": "Days Since Purchase",
            "purchase_count": "Purchases",
            "lifetime_revenue": "Lifetime Revenue",
            "current_12m_revenue": "Current 12M",
            "prior_12m_revenue": "Prior 12M",
            "reference_opportunity_value": "Reference Opportunity",
            "action_reason": "Why Review",
        }
    )

    st.dataframe(
        display_queue,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lifetime Revenue": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Current 12M": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Prior 12M": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Reference Opportunity": st.column_config.NumberColumn(
                format="$%d",
            ),
        },
    )

    st.caption(
        f"Showing {len(display_queue):,} customers based on the selected "
        "priority filters."
    )

with tab2:
    st.subheader("Opportunity Segment Summary")

    summary_display = summary.rename(
        columns={
            "priority_segment": "Priority Segment",
            "customers": "Customers",
            "lifetime_revenue": "Lifetime Revenue",
            "reference_opportunity_value": "Reference Opportunity",
        }
    )

    st.dataframe(
        summary_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lifetime Revenue": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Reference Opportunity": st.column_config.NumberColumn(
                format="$%d",
            ),
        },
    )

    st.bar_chart(
        summary.set_index(
            "priority_segment"
        )["customers"]
    )

    st.markdown(
        """
        **Priority interpretation**

        - **A-DUAL:** high-value customer with both cycle and decline signals
        - **A-CYCLE:** high-value customer appears due based on purchase cadence
        - **A-DECLINE:** high-value customer shows material recent revenue decline
        - **B-CYCLE:** repeat-purchase pattern suggests follow-up
        - **B-DECLINE:** recent revenue trails the prior period materially
        - **B-INACTIVE:** no purchase within the last 12 months
        - **C-NURTURE:** maintain relationship and monitor
        """
    )

with tab3:
    st.subheader("Sales Rep & Store Opportunity Views")

    left, right = st.columns(2)

    with left:
        rep = (
            actionable.groupby(
                "salesperson",
                as_index=False,
            )
            .agg(
                customers=("customer_id", "nunique"),
                priority_a=(
                    "priority_segment",
                    lambda s: s.str.startswith("A-").sum(),
                ),
                reference_opportunity_value=(
                    "reference_opportunity_value",
                    "sum",
                ),
            )
            .sort_values(
                "reference_opportunity_value",
                ascending=False,
            )
        )

        st.markdown("### Sales Rep Queue")

        st.bar_chart(
            rep.set_index(
                "salesperson"
            )["reference_opportunity_value"]
        )

        st.dataframe(
            rep.rename(
                columns={
                    "salesperson": "Sales Rep",
                    "customers": "Actionable Customers",
                    "priority_a": "Priority A",
                    "reference_opportunity_value": "Reference Opportunity",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Reference Opportunity": st.column_config.NumberColumn(
                    format="$%d",
                ),
            },
        )

    with right:
        store = (
            actionable.groupby(
                "store",
                as_index=False,
            )
            .agg(
                customers=("customer_id", "nunique"),
                priority_a=(
                    "priority_segment",
                    lambda s: s.str.startswith("A-").sum(),
                ),
                reference_opportunity_value=(
                    "reference_opportunity_value",
                    "sum",
                ),
            )
            .sort_values(
                "reference_opportunity_value",
                ascending=False,
            )
        )

        st.markdown("### Store Queue")

        st.bar_chart(
            store.set_index(
                "store"
            )["reference_opportunity_value"]
        )

        st.dataframe(
            store.rename(
                columns={
                    "store": "Store",
                    "customers": "Actionable Customers",
                    "priority_a": "Priority A",
                    "reference_opportunity_value": "Reference Opportunity",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Reference Opportunity": st.column_config.NumberColumn(
                    format="$%d",
                ),
            },
        )

with tab4:
    st.subheader("Customer Signal Diagnostics")

    signal_counts = pd.DataFrame(
        {
            "Signal": [
                "High Value",
                "Revenue Decline",
                "Purchase Cycle Due",
                "Purchase Cycle Overdue",
                "Inactive > 12 Months",
                "Dormant > 18 Months",
            ],
            "Customers": [
                int(customers["high_value_customer"].sum()),
                int(customers["revenue_decline_flag"].sum()),
                int(customers["purchase_cycle_due"].sum()),
                int(customers["purchase_cycle_overdue"].sum()),
                int(customers["inactive_flag"].sum()),
                int(customers["dormant_flag"].sum()),
            ],
        }
    )

    st.bar_chart(
        signal_counts.set_index(
            "Signal"
        )["Customers"]
    )

    st.dataframe(
        signal_counts,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Signals can overlap. One customer may simultaneously be high-value, "
        "declining, and due based on purchase cadence."
    )

st.divider()
st.subheader("Download Sales Action Queue")

download_cols = [
    "customer_id",
    "display_name",
    "store",
    "salesperson",
    "priority_segment",
    "days_since_last_purchase",
    "purchase_count",
    "lifetime_revenue",
    "current_12m_revenue",
    "prior_12m_revenue",
    "revenue_change",
    "revenue_change_pct",
    "avg_purchase_interval_days",
    "cycle_ratio",
    "reference_opportunity_value",
    "action_reason",
]

download_df = queue[
    download_cols
].copy()

csv_data = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Customer Action Queue as CSV",
    data=csv_data,
    file_name="customer_revenue_opportunity_queue.csv",
    mime="text/csv",
)

with st.expander("Methodology & Guardrails"):
    st.markdown(
        """
        ### What the engine does

        1. Aggregates synthetic transactions at the customer level.
        2. Measures recency, purchase frequency, lifetime revenue, and average value.
        3. Compares the most recent 12 months with the prior 12 months.
        4. Calculates historical days between repeat purchases.
        5. Detects purchase-cycle, inactivity, dormancy, and revenue-decline signals.
        6. Combines those signals using transparent A/B/C rules.
        7. Produces a prioritized sales-action queue.

        ### What the engine does not claim

        - A priority segment does **not** guarantee that a customer will buy.
        - Reference opportunity value is **not** forecast revenue.
        - Dormancy does **not** mean a customer has permanently churned.
        - Revenue decline may have operational explanations outside the dataset.
        - Sales teams should combine these signals with customer context,
          product availability, seasonality, and relationship knowledge.

        ### Data safety

        All customers, companies, transactions, stores, products, and values
        in this public demo are synthetic and generated in `engine/demo_data.py`.
        """
    )

st.caption(
    "Portfolio project by Alex Monday • Python • pandas • Streamlit • "
    "customer analytics • revenue operations • lifecycle intelligence • "
    "sales prioritization"
)
