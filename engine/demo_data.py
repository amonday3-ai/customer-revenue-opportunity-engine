"""Deterministic synthetic customer sales history for the public portfolio demo."""

from __future__ import annotations

from datetime import date, timedelta
import random

import pandas as pd


FIRST_NAMES = [
    "Jordan", "Taylor", "Morgan", "Casey", "Riley",
    "Cameron", "Avery", "Drew", "Logan", "Parker",
]

LAST_NAMES = [
    "Carter", "Brooks", "Hayes", "Reed", "Bennett",
    "Collins", "Foster", "Turner", "Perry", "Morgan",
]

COMPANY_WORDS = [
    "Landscaping",
    "Farms",
    "Outdoor Services",
    "Property Care",
    "Construction",
    "Maintenance",
    "Excavating",
    "Lawn & Snow",
]

PRODUCTS = [
    ("Zero Turn Mower", 7800),
    ("Compact Tractor", 24500),
    ("Utility Vehicle", 16800),
    ("ATV", 9400),
    ("Snow Equipment", 4200),
    ("Commercial Mower", 11200),
]

STORES = [
    "Grand River",
    "Lakeview",
    "Northfield",
    "Pine Ridge",
]


def _random_purchase_date(
    rng: random.Random,
    start: date,
    end: date,
) -> date:
    """Return a deterministic random date between two dates."""

    total_days = (end - start).days

    offset = rng.randint(
        0,
        max(total_days, 0),
    )

    return start + timedelta(days=offset)


def build_demo_customer_history(
    seed: int = 4712,
    customer_count: int = 600,
    analysis_date: date = date(2026, 9, 9),
) -> pd.DataFrame:
    """
    Generate synthetic multi-year customer purchase history.

    Customer behavior intentionally includes:
    - active repeat buyers,
    - dormant customers,
    - declining customers,
    - high-value accounts,
    - single-purchase customers,
    - purchase-cycle opportunities.

    No employer or real customer data is represented.
    """

    rng = random.Random(seed)

    rows = []

    transaction_id = 100000

    history_start = date(
        analysis_date.year - 5,
        1,
        1,
    )

    for customer_number in range(
        1,
        customer_count + 1,
    ):

        customer_id = (
            f"CUST-{customer_number:05d}"
        )

        customer_type = customer_number % 7

        first_name = FIRST_NAMES[
            customer_number
            % len(FIRST_NAMES)
        ]

        last_name = LAST_NAMES[
            (
                customer_number * 3
            )
            % len(LAST_NAMES)
        ]

        is_business = (
            customer_number % 4 == 0
        )

        if is_business:
            company_name = (
                f"{last_name} "
                f"{COMPANY_WORDS[customer_number % len(COMPANY_WORDS)]}"
            )
        else:
            company_name = ""

        store = STORES[
            customer_number
            % len(STORES)
        ]

        # -------------------------------------------------------------
        # CUSTOMER BEHAVIOR PROFILES
        # -------------------------------------------------------------
        if customer_type == 0:
            # High-value repeat customer
            purchase_count = rng.randint(
                6,
                10,
            )

            value_multiplier = rng.uniform(
                1.25,
                1.75,
            )

            recent_bias = True

        elif customer_type == 1:
            # Dormant high-value customer
            purchase_count = rng.randint(
                3,
                6,
            )

            value_multiplier = rng.uniform(
                1.20,
                1.65,
            )

            recent_bias = False

        elif customer_type == 2:
            # Declining customer
            purchase_count = rng.randint(
                5,
                8,
            )

            value_multiplier = rng.uniform(
                0.95,
                1.30,
            )

            recent_bias = True

        elif customer_type == 3:
            # Purchase-cycle opportunity
            purchase_count = rng.randint(
                3,
                5,
            )

            value_multiplier = rng.uniform(
                1.00,
                1.40,
            )

            recent_bias = False

        elif customer_type == 4:
            # Active moderate-value customer
            purchase_count = rng.randint(
                3,
                6,
            )

            value_multiplier = rng.uniform(
                0.85,
                1.20,
            )

            recent_bias = True

        elif customer_type == 5:
            # One-time buyer
            purchase_count = 1

            value_multiplier = rng.uniform(
                0.80,
                1.15,
            )

            recent_bias = False

        else:
            # Low-frequency historical buyer
            purchase_count = rng.randint(
                2,
                4,
            )

            value_multiplier = rng.uniform(
                0.75,
                1.10,
            )

            recent_bias = False

        purchase_dates = []

        # -------------------------------------------------------------
        # PURCHASE DATE GENERATION
        # -------------------------------------------------------------
        if customer_type == 1:
            # Force dormant behavior:
            # all purchases end roughly 18-36 months ago.
            dormant_end = (
                analysis_date
                - timedelta(
                    days=rng.randint(
                        540,
                        1080,
                    )
                )
            )

            for _ in range(
                purchase_count
            ):
                purchase_dates.append(
                    _random_purchase_date(
                        rng,
                        history_start,
                        dormant_end,
                    )
                )

        elif customer_type == 3:
            # Repeat purchase cadence around 12-18 months.
            interval_days = rng.randint(
                360,
                540,
            )

            last_purchase = (
                analysis_date
                - timedelta(
                    days=interval_days
                    + rng.randint(
                        -60,
                        90,
                    )
                )
            )

            for index in range(
                purchase_count
            ):
                purchase_date = (
                    last_purchase
                    - timedelta(
                        days=(
                            interval_days
                            * (
                                purchase_count
                                - index
                                - 1
                            )
                        )
                    )
                )

                if purchase_date >= history_start:
                    purchase_dates.append(
                        purchase_date
                    )

        else:
            for _ in range(
                purchase_count
            ):
                if recent_bias:
                    start = (
                        analysis_date
                        - timedelta(
                            days=1095
                        )
                    )

                    start = max(
                        start,
                        history_start,
                    )

                else:
                    start = history_start

                purchase_dates.append(
                    _random_purchase_date(
                        rng,
                        start,
                        analysis_date,
                    )
                )

        purchase_dates = sorted(
            purchase_dates
        )

        # -------------------------------------------------------------
        # PURCHASE TRANSACTIONS
        # -------------------------------------------------------------
        for index, purchase_date in enumerate(
            purchase_dates
        ):

            transaction_id += 1

            product_name, base_value = (
                PRODUCTS[
                    (
                        customer_number
                        + index
                    )
                    % len(PRODUCTS)
                ]
            )

            sale_value = (
                base_value
                * value_multiplier
                * rng.uniform(
                    0.88,
                    1.12,
                )
            )

            # Create revenue decline behavior.
            if (
                customer_type == 2
                and purchase_count > 1
            ):
                decline_factor = (
                    1
                    - (
                        index
                        / purchase_count
                    )
                    * 0.45
                )

                sale_value *= (
                    decline_factor
                )

            salesperson = (
                "Sales Rep "
                + str(
                    (
                        customer_number
                        % 5
                    )
                    + 1
                )
            )

            rows.append(
                {
                    "transaction_id": (
                        f"DEMO-{transaction_id}"
                    ),
                    "customer_id": customer_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company_name": company_name,
                    "store": store,
                    "salesperson": salesperson,
                    "purchase_date": (
                        purchase_date.isoformat()
                    ),
                    "product": product_name,
                    "sale_value": round(
                        sale_value,
                        2,
                    ),
                }
            )

    history = pd.DataFrame(
        rows
    )

    history[
        "purchase_date"
    ] = pd.to_datetime(
        history[
            "purchase_date"
        ]
    )

    history = (
        history.sort_values(
            [
                "customer_id",
                "purchase_date",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    return history
