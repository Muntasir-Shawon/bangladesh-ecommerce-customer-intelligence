"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/analytics/cohorts.py
Purpose: Generates monthly customer acquisition cohort matrices, retention rates,
         and revenue retention heatmaps.
"""

import pandas as pd
import numpy as np
from typing import Tuple


def compute_cohort_retention_matrix(df_ord: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Computes:
    1. Absolute customer counts retention matrix
    2. Percentage retention rate matrix (M0=100%, M1, M2...)
    3. Revenue retention matrix
    """
    delivered = df_ord[df_ord["order_status"] == "Delivered"].copy()
    delivered["order_month"] = delivered["order_date"].dt.to_period("M")

    # Determine cohort (first purchase month) per customer
    customer_cohort = delivered.groupby("customer_id")["order_month"].min().reset_index()
    customer_cohort.rename(columns={"order_month": "cohort_month"}, inplace=True)

    merged = delivered.merge(customer_cohort, on="customer_id")
    
    # Calculate period offset
    merged["cohort_index"] = (
        (merged["order_month"].dt.year - merged["cohort_month"].dt.year) * 12 +
        (merged["order_month"].dt.month - merged["cohort_month"].dt.month)
    )

    # 1. Customer Counts Matrix
    cohort_counts = merged.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
    count_pivot = cohort_counts.pivot(index="cohort_month", columns="cohort_index", values="customer_id")

    # 2. Percentage Retention Matrix
    cohort_sizes = count_pivot.iloc[:, 0]
    retention_pivot = count_pivot.divide(cohort_sizes, axis=0) * 100

    # 3. Revenue Retention Matrix
    cohort_rev = merged.groupby(["cohort_month", "cohort_index"])["total_amount"].sum().reset_index()
    revenue_pivot = cohort_rev.pivot(index="cohort_month", columns="cohort_index", values="total_amount")

    return count_pivot, retention_pivot, revenue_pivot
