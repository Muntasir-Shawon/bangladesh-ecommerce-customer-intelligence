"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/clv/clv_model.py
Purpose: Comprehensive Customer Lifetime Value (CLV) modeling engine:
         - Historical Realized CLV
         - Predictive Formulaic CLV (Margin, Frequency, Retention Rate)
         - Discounted Cash Flow CLV (DCF)
         - CLV by RFM Segment, Acquisition Channel, and Division
         - LTV:CAC Ratio Analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

# Estimated CAC (Customer Acquisition Cost in BDT) in Bangladesh
ESTIMATED_CAC_BDT = {
    "Facebook Ads": 320.0,
    "Google Ads": 420.0,
    "TikTok / Instagram": 260.0,
    "Organic Search": 60.0,
    "Referral": 80.0,
    "Direct / Offline": 40.0
}


def calculate_customer_clv_metrics(
    df_cust: pd.DataFrame,
    df_ord: pd.DataFrame,
    df_items: pd.DataFrame,
    annual_discount_rate: float = 0.10,
    observation_months: float = 33.0  # 2.75 years
) -> pd.DataFrame:
    """
    Computes both Historical CLV and Forward-Looking Predictive CLV per customer.
    """
    delivered = df_ord[df_ord["order_status"] == "Delivered"].copy()
    items_delivered = df_items.merge(delivered[["order_id", "customer_id", "order_date"]], on="order_id")

    # 1. Historical Realized Financials per customer
    cust_fin = items_delivered.groupby("customer_id").agg(
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
        total_orders=("order_id", "nunique"),
        historical_revenue=("revenue", "sum"),
        historical_cost=("cost", "sum"),
        historical_profit=("profit", "sum")
    ).reset_index()

    cust_fin["historical_margin_pct"] = (cust_fin["historical_profit"] / cust_fin["historical_revenue"] * 100).round(2)
    cust_fin["aov"] = (cust_fin["historical_revenue"] / cust_fin["total_orders"]).round(2)

    # Lifespan in months
    cust_fin["tenure_months"] = (
        (pd.to_datetime(cust_fin["last_order_date"]) - pd.to_datetime(cust_fin["first_order_date"])).dt.days / 30.44
    ).clip(lower=1.0).round(1)

    # Monthly purchase frequency
    cust_fin["monthly_purchase_frequency"] = (cust_fin["total_orders"] / cust_fin["tenure_months"]).clip(upper=4.0)

    # Retention probability heuristic based on recency
    max_date = delivered["order_date"].max()
    cust_fin["recency_days"] = (pd.to_datetime(max_date) - pd.to_datetime(cust_fin["last_order_date"])).dt.days
    
    # Sigmoid / exponential decay of retention based on recency
    cust_fin["retention_rate"] = np.exp(-cust_fin["recency_days"] / 180.0).clip(0.05, 0.95).round(3)
    cust_fin["churn_rate"] = (1.0 - cust_fin["retention_rate"]).round(3)

    # Predictive CLV formula:
    # 24-Month Forward-looking CLV with monthly discount rate
    monthly_discount = (1 + annual_discount_rate) ** (1 / 12) - 1
    monthly_profit_run_rate = (cust_fin["aov"] * cust_fin["monthly_purchase_frequency"] * (cust_fin["historical_margin_pct"] / 100))

    # Geometric series for discounted future value across 24 months:
    # PV = sum_{t=1}^{24} (monthly_profit * (retention_rate / (1 + discount))^t)
    effective_decay = (cust_fin["retention_rate"] / (1 + monthly_discount)).values
    
    # Vectorized 24-month horizon calculation
    periods = np.arange(1, 25)
    pv_factors = np.array([effective_decay ** t for t in periods]).sum(axis=0)
    
    cust_fin["predictive_24m_clv_profit"] = (monthly_profit_run_rate * pv_factors).round(2)
    cust_fin["total_expected_clv"] = (cust_fin["historical_profit"] + cust_fin["predictive_24m_clv_profit"]).round(2)

    # Merge with demographics
    merged = df_cust.merge(cust_fin, on="customer_id", how="inner")
    merged["cac_bdt"] = merged["acquisition_channel"].map(ESTIMATED_CAC_BDT).fillna(150.0)
    merged["clv_to_cac_ratio"] = (merged["total_expected_clv"] / merged["cac_bdt"]).round(2)

    return merged


def clv_breakdown_by_channel(df_clv: pd.DataFrame) -> pd.DataFrame:
    """Aggregates CLV and LTV:CAC efficiency by marketing channel."""
    summary = df_clv.groupby("acquisition_channel").agg(
        customer_count=("customer_id", "count"),
        avg_historical_revenue=("historical_revenue", "mean"),
        avg_historical_profit=("historical_profit", "mean"),
        avg_predictive_clv=("predictive_24m_clv_profit", "mean"),
        avg_total_clv=("total_expected_clv", "mean"),
        cac_bdt=("cac_bdt", "first")
    ).reset_index()

    summary["ltv_cac_ratio"] = (summary["avg_total_clv"] / summary["cac_bdt"]).round(2)
    summary["avg_historical_revenue"] = summary["avg_historical_revenue"].round(2)
    summary["avg_historical_profit"] = summary["avg_historical_profit"].round(2)
    summary["avg_predictive_clv"] = summary["avg_predictive_clv"].round(2)
    summary["avg_total_clv"] = summary["avg_total_clv"].round(2)

    return summary.sort_values(by="ltv_cac_ratio", ascending=False).reset_index(drop=True)
