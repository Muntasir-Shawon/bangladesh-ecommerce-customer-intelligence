"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/segmentation/rfm.py
Purpose: Professional RFM (Recency, Frequency, Monetary) segmentation engine
         with quintile scoring and strategic customer persona mapping.
"""

import datetime
import numpy as np
import pandas as pd
from typing import Tuple, Dict


def calculate_rfm(df_ord: pd.DataFrame, reference_date: datetime.date = None) -> pd.DataFrame:
    """
    Computes Recency, Frequency, Monetary values per customer.
    - Recency: Days since last delivered purchase
    - Frequency: Total distinct delivered orders
    - Monetary: Total customer spending in BDT
    """
    delivered = df_ord[df_ord["order_status"] == "Delivered"].copy()
    if reference_date is None:
        # Default reference date: day after latest order
        reference_date = delivered["order_date"].max() + datetime.timedelta(days=1)

    rfm = delivered.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        first_order_date=("order_date", "min"),
        frequency=("order_id", "nunique"),
        monetary=("total_amount", "sum")
    ).reset_index()

    rfm["recency"] = (pd.to_datetime(reference_date) - pd.to_datetime(rfm["last_order_date"])).dt.days
    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["aov"] = (rfm["monetary"] / rfm["frequency"]).round(2)
    rfm["tenure_days"] = (pd.to_datetime(reference_date) - pd.to_datetime(rfm["first_order_date"])).dt.days

    return rfm


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns quintile scores (1 to 5) to Recency, Frequency, and Monetary.
    - Recency: Lower days = Higher Score (5)
    - Frequency: Higher count = Higher Score (5)
    - Monetary: Higher spending = Higher Score (5)
    """
    df = rfm.copy()

    # Recency scoring: 1 (worst, longest ago) to 5 (best, most recent)
    df["r_score"] = pd.qcut(df["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)

    # Frequency scoring: use rank method 'first' to handle tied discrete counts cleanly
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Monetary scoring
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    df["rfm_score"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)
    df["rfm_combined_score"] = df["r_score"] + df["f_score"] + df["m_score"]

    return df


def assign_rfm_segments(df_scored: pd.DataFrame) -> pd.DataFrame:
    """
    Maps RFM score patterns into actionable business customer segments:
    - Champions: High recency, high frequency, high spend
    - Loyal Customers: Responsive, repeat buyers
    - Potential Loyalists: Recent buyers with moderate spend
    - New Customers: High recency, low frequency
    - Promising Customers: Recent buyers who spent moderately
    - At Risk: Formerly loyal, haven't purchased in a while
    - Cannot Lose Them: High spenders who haven't purchased recently
    - Hibernating: Low recency, low frequency
    - Lost Customers: Lowest recency and lowest spend
    """
    df = df_scored.copy()

    def segment_logic(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]

        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f in [2, 3]:
            return "Potential Loyalists"
        elif r == 5 and f == 1:
            return "New Customers"
        elif r == 4 and f == 1:
            return "Promising Customers"
        elif r <= 2 and f >= 4:
            return "Cannot Lose Them"
        elif r <= 2 and f == 3:
            return "At Risk"
        elif r <= 2 and f == 2:
            return "Hibernating"
        else:
            return "Lost Customers"

    df["rfm_segment"] = df.apply(segment_logic, axis=1)
    return df


def generate_rfm_summary(df_segmented: pd.DataFrame) -> pd.DataFrame:
    """Generates business KPI summary table per RFM customer segment."""
    summary = df_segmented.groupby("rfm_segment").agg(
        customer_count=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        total_monetary=("monetary", "sum"),
        avg_aov=("aov", "mean")
    ).reset_index()

    total_customers = len(df_segmented)
    total_rev = df_segmented["monetary"].sum()

    summary["pct_customers"] = (summary["customer_count"] / total_customers * 100).round(2)
    summary["pct_revenue"] = (summary["total_monetary"] / total_rev * 100).round(2)
    summary["avg_recency"] = summary["avg_recency"].round(1)
    summary["avg_frequency"] = summary["avg_frequency"].round(2)
    summary["avg_monetary"] = summary["avg_monetary"].round(2)
    summary["total_monetary"] = summary["total_monetary"].round(2)
    summary["avg_aov"] = summary["avg_aov"].round(2)

    return summary.sort_values(by="total_monetary", ascending=False).reset_index(drop=True)
