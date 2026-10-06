"""
Unit tests for RFM calculations, quintile scoring, and segmentation.
"""

import os
import pytest
import pandas as pd
from src.segmentation.rfm import calculate_rfm, score_rfm, assign_rfm_segments

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


@pytest.fixture
def sample_orders():
    df_ord = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "orders.csv"))
    df_ord["order_date"] = pd.to_datetime(df_ord["order_date"])
    return df_ord


def test_rfm_calculation(sample_orders):
    rfm = calculate_rfm(sample_orders)
    assert "recency" in rfm.columns
    assert "frequency" in rfm.columns
    assert "monetary" in rfm.columns
    assert (rfm["recency"] < 0).sum() == 0, "Recency cannot be negative!"
    assert (rfm["frequency"] < 1).sum() == 0, "Purchasing customers must have at least 1 order!"
    assert (rfm["monetary"] <= 0).sum() == 0, "Monetary spend must be positive!"


def test_rfm_scoring_and_segmentation(sample_orders):
    rfm = calculate_rfm(sample_orders)
    scored = score_rfm(rfm)
    assert set(scored["r_score"].unique()).issubset({1, 2, 3, 4, 5})
    assert set(scored["f_score"].unique()).issubset({1, 2, 3, 4, 5})
    assert set(scored["m_score"].unique()).issubset({1, 2, 3, 4, 5})

    segmented = assign_rfm_segments(scored)
    assert "rfm_segment" in segmented.columns
    valid_segments = {
        "Champions", "Loyal Customers", "Potential Loyalists", "New Customers",
        "Promising Customers", "At Risk", "Cannot Lose Them", "Hibernating", "Lost Customers"
    }
    assert set(segmented["rfm_segment"].unique()).issubset(valid_segments)
