"""
Unit tests for Customer Lifetime Value (CLV) calculations and unit economics.
"""

import os
import pytest
import pandas as pd
from src.clv.clv_model import calculate_customer_clv_metrics, clv_breakdown_by_channel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


@pytest.fixture
def clean_data():
    df_cust = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "customers.csv"))
    df_ord = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "orders.csv"))
    df_items = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "order_items.csv"))
    df_ord["order_date"] = pd.to_datetime(df_ord["order_date"])
    return df_cust, df_ord, df_items


def test_clv_computation(clean_data):
    df_cust, df_ord, df_items = clean_data
    df_clv = calculate_customer_clv_metrics(df_cust, df_ord, df_items)

    assert "historical_profit" in df_clv.columns
    assert "predictive_24m_clv_profit" in df_clv.columns
    assert "total_expected_clv" in df_clv.columns
    assert "clv_to_cac_ratio" in df_clv.columns

    # Average total expected CLV should be positive
    assert df_clv["total_expected_clv"].mean() > 0
    assert (df_clv["cac_bdt"] <= 0).sum() == 0, "CAC must be positive!"


def test_channel_breakdown(clean_data):
    df_cust, df_ord, df_items = clean_data
    df_clv = calculate_customer_clv_metrics(df_cust, df_ord, df_items)
    channel_summary = clv_breakdown_by_channel(df_clv)

    assert len(channel_summary) > 0
    assert "ltv_cac_ratio" in channel_summary.columns
    assert channel_summary["ltv_cac_ratio"].min() > 0
