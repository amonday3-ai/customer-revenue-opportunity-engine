"""Core analysis functions for the Customer Revenue Opportunity Engine."""

from .analysis import (
    analyze_customers,
    build_action_queue,
    segment_summary,
)
from .demo_data import build_demo_customer_history

__all__ = [
    "analyze_customers",
    "build_action_queue",
    "segment_summary",
    "build_demo_customer_history",
]
