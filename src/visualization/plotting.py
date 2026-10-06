"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/visualization/plotting.py
Purpose: Reusable visualization utilities with clean styling for analytics reporting.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Configure standard visual aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def plot_revenue_trend(df_monthly: pd.DataFrame, output_path: str = None):
    """Plots monthly revenue and profit trends with seasonal markers."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df_monthly["month"], df_monthly["monthly_revenue"] / 1e6, marker="o", color="#1f77b4", linewidth=2.5, label="Revenue (Million BDT)")
    ax1.plot(df_monthly["month"], df_monthly["monthly_profit"] / 1e6, marker="s", color="#2ca02c", linewidth=2, linestyle="--", label="Gross Profit (Million BDT)")

    ax1.set_title("Monthly Revenue & Gross Profit Trajectory (Bangladesh E-Commerce)", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Month", fontsize=11)
    ax1.set_ylabel("Million BDT", fontsize=11)
    ax1.tick_params(axis="x", rotation=45)
    ax1.legend(loc="upper left")

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
    plt.close()


def plot_rfm_segments(df_rfm_summary: pd.DataFrame, output_path: str = None):
    """Bar chart comparing customer share vs revenue share across RFM segments."""
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(df_rfm_summary))
    width = 0.38

    ax.bar(x - width/2, df_rfm_summary["pct_customers"], width, label="% of Customers", color="#4e79a7")
    ax.bar(x + width/2, df_rfm_summary["pct_revenue"], width, label="% of Total Revenue", color="#f28e2b")

    ax.set_title("RFM Customer Segment Distribution vs Revenue Contribution", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(df_rfm_summary["rfm_segment"], rotation=30, ha="right", fontsize=10)
    ax.set_ylabel("Percentage (%)", fontsize=11)
    ax.legend(loc="upper right")

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
    plt.close()


def plot_cohort_heatmap(retention_pivot: pd.DataFrame, output_path: str = None):
    """Heatmap of monthly cohort retention matrix."""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Mask upper triangle
    mask = retention_pivot.isnull()

    sns.heatmap(
        retention_pivot,
        mask=mask,
        annot=True,
        fmt=".1f",
        cmap="Blues",
        vmin=0,
        vmax=100,
        cbar_kws={"label": "Retention Rate (%)"},
        ax=ax
    )

    ax.set_title("Customer Cohort Retention Rate (%) Across Lifecycle Months", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Cohort Lifecycle Month (M0 = First Purchase)", fontsize=11)
    ax.set_ylabel("Acquisition Cohort (Month)", fontsize=11)

    plt.tight_layout()
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
    plt.close()
