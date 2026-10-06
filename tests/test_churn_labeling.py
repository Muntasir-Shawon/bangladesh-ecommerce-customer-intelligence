"""
Unit tests for leakage-free churn dataset construction and feature engineering.
"""

import os
import pytest
import pandas as pd
from src.churn.model import create_leakage_free_churn_dataset

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def test_leakage_free_churn_dataset():
    df_cust = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "customers.csv"))
    df_prod = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "products.csv"))
    df_ord = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "orders.csv"))
    df_items = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "order_items.csv"))

    df_ord["order_date"] = pd.to_datetime(df_ord["order_date"])

    X, y, full_df = create_leakage_free_churn_dataset(
        df_cust, df_ord, df_items, df_prod, cutoff_days=90
    )

    # Assertions
    assert len(X) == len(y), "Features and target must have identical row count!"
    assert set(y.unique()).issubset({0, 1}), "Churn target must be strictly binary (0 or 1)!"
    assert (X["recency_days"] < 0).sum() == 0, "Recency relative to cutoff cannot be negative!"
    assert (X["total_orders"] < 1).sum() == 0, "Customers in feature set must have >=1 order prior to cutoff!"
    assert not X.isnull().any().any(), "Features matrix must have zero unhandled null values!"
