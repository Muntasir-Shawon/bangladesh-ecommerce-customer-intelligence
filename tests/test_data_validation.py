"""
Unit tests for data validation, cleaning, and constraints.
"""

import os
import pytest
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def test_processed_files_exist():
    expected_files = ["customers.csv", "products.csv", "orders.csv", "order_items.csv"]
    for f in expected_files:
        path = os.path.join(PROCESSED_DATA_DIR, f)
        assert os.path.exists(path), f"File {f} is missing from processed directory!"


def test_customer_constraints():
    df_cust = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "customers.csv"))
    assert df_cust["customer_id"].is_unique, "Customer IDs must be unique!"
    assert df_cust["customer_id"].isnull().sum() == 0, "Customer IDs cannot be null!"
    assert (df_cust["age"] < 18).sum() == 0, "No customer can be under 18 years old!"
    assert (df_cust["age"] > 80).sum() == 0, "No customer can be over 80 years old!"
    assert set(df_cust["gender"].unique()).issubset({"Male", "Female", "Unknown"}), "Invalid gender detected!"


def test_product_pricing_constraints():
    df_prod = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "products.csv"))
    assert df_prod["product_id"].is_unique, "Product IDs must be unique!"
    assert (df_prod["cost_price"] <= 0).sum() == 0, "Cost price must be positive!"
    assert (df_prod["selling_price"] < df_prod["cost_price"]).sum() == 0, "Selling price must exceed cost price!"


def test_order_items_integrity():
    df_items = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "order_items.csv"))
    assert df_items["order_item_id"].is_unique, "Order Item IDs must be unique!"
    assert (df_items["quantity"] <= 0).sum() == 0, "Quantities must be positive!"
    assert (df_items["unit_price"] <= 0).sum() == 0, "Unit prices must be positive!"
    assert (df_items["revenue"] < 0).sum() == 0, "Revenue cannot be negative!"
