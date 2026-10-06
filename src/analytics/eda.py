"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/analytics/eda.py
Purpose: Statistical and exploratory data analysis functions for customer behavior,
         revenue dynamics, category margins, and regional distributions.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def load_curated_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Loads all four cleaned datasets from processed CSVs."""
    df_cust = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "customers.csv"))
    df_prod = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "products.csv"))
    df_ord = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "orders.csv"))
    df_items = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "order_items.csv"))

    df_cust["signup_date"] = pd.to_datetime(df_cust["signup_date"])
    df_ord["order_date"] = pd.to_datetime(df_ord["order_date"])
    return df_cust, df_prod, df_ord, df_items


def compute_spending_summary(df_ord: pd.DataFrame) -> Dict[str, float]:
    """Calculates key customer spending summary statistics."""
    delivered = df_ord[df_ord["order_status"] == "Delivered"]
    spend_per_cust = delivered.groupby("customer_id")["total_amount"].sum()

    return {
        "mean_spend_bdt": float(spend_per_cust.mean()),
        "median_spend_bdt": float(spend_per_cust.median()),
        "std_spend_bdt": float(spend_per_cust.std()),
        "p25_spend_bdt": float(spend_per_cust.quantile(0.25)),
        "p75_spend_bdt": float(spend_per_cust.quantile(0.75)),
        "p90_spend_bdt": float(spend_per_cust.quantile(0.90)),
        "p99_spend_bdt": float(spend_per_cust.quantile(0.99)),
        "max_spend_bdt": float(spend_per_cust.max()),
        "skewness": float(spend_per_cust.skew()),
        "kurtosis": float(spend_per_cust.kurt())
    }


def compute_pareto_distribution(df_ord: pd.DataFrame) -> pd.DataFrame:
    """Computes cumulative revenue concentration to evaluate the 80/20 rule."""
    delivered = df_ord[df_ord["order_status"] == "Delivered"]
    cust_rev = delivered.groupby("customer_id")["total_amount"].sum().reset_index()
    cust_rev = cust_rev.sort_values(by="total_amount", ascending=False).reset_index(drop=True)

    total_revenue = cust_rev["total_amount"].sum()
    total_customers = len(cust_rev)

    cust_rev["customer_rank"] = cust_rev.index + 1
    cust_rev["cumulative_customer_pct"] = (cust_rev["customer_rank"] / total_customers) * 100
    cust_rev["cumulative_revenue"] = cust_rev["total_amount"].cumsum()
    cust_rev["cumulative_revenue_pct"] = (cust_rev["cumulative_revenue"] / total_revenue) * 100

    return cust_rev


def perform_statistical_hypothesis_tests(df_cust: pd.DataFrame, df_ord: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes formal statistical hypothesis testing:
    1. Two-sample Mann-Whitney U test: Spending difference between Dhaka vs Non-Dhaka.
    2. Kruskal-Wallis H test: Order values across major Acquisition Channels.
    3. Chi-square test of independence: Payment method preference vs Customer Type.
    """
    delivered = df_ord[df_ord["order_status"] == "Delivered"].copy()
    merged = delivered.merge(df_cust, on="customer_id")

    # 1. Dhaka vs Outside Dhaka Spending
    dhaka_spend = merged[merged["division"] == "Dhaka"]["total_amount"]
    outside_spend = merged[merged["division"] != "Dhaka"]["total_amount"]
    u_stat, u_pval = stats.mannwhitneyu(dhaka_spend, outside_spend, alternative="two-sided")

    # 2. Acquisition Channel Order Values (Kruskal-Wallis)
    channels = merged["acquisition_channel"].unique()
    channel_groups = [merged[merged["acquisition_channel"] == ch]["total_amount"].values for ch in channels]
    h_stat, h_pval = stats.kruskal(*channel_groups)

    # 3. Payment Method vs Customer Type (Chi-Square)
    contingency_table = pd.crosstab(merged["payment_method"], merged["customer_type"])
    chi2_stat, chi2_pval, dof, _ = stats.chi2_contingency(contingency_table)

    return {
        "mann_whitney_dhaka_vs_outside": {
            "statistic": float(u_stat),
            "p_value": float(u_pval),
            "dhaka_median": float(dhaka_spend.median()),
            "outside_median": float(outside_spend.median()),
            "significant_at_005": bool(u_pval < 0.05)
        },
        "kruskal_acquisition_channel": {
            "statistic": float(h_stat),
            "p_value": float(h_pval),
            "significant_at_005": bool(h_pval < 0.05)
        },
        "chi2_payment_vs_cust_type": {
            "statistic": float(chi2_stat),
            "p_value": float(chi2_pval),
            "dof": int(dof),
            "significant_at_005": bool(chi2_pval < 0.05)
        }
    }


if __name__ == "__main__":
    cust, prod, ords, items = load_curated_data()
    print("Spending Stats:", compute_spending_summary(ords))
    tests = perform_statistical_hypothesis_tests(cust, ords)
    print("Hypothesis Testing Results:")
    for k, v in tests.items():
        print(f" - {k}: {v}")
