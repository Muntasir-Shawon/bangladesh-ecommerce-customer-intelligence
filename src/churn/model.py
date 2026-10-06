"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/churn/model.py
Purpose: Machine Learning pipeline for customer churn prediction:
         - Leakage-free temporal cutoff (Observation Window vs Feature Window)
         - Comprehensive feature engineering
         - Training & comparison: Logistic Regression, Random Forest, XGBoost
         - Evaluation: ROC-AUC, PR-AUC, Precision, Recall, F1, Confusion Matrix
         - Optimal threshold selection
"""

import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, classification_report
)


def create_leakage_free_churn_dataset(
    df_cust: pd.DataFrame,
    df_ord: pd.DataFrame,
    df_items: pd.DataFrame,
    df_prod: pd.DataFrame,
    cutoff_days: int = 90
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Creates a churn dataset strictly avoiding temporal data leakage:
    - Observation Window: [Cutoff Date, Max Dataset Date]
    - Feature Window: (-inf, Cutoff Date]
    Target (Churn): 1 if customer placed NO orders in the Observation Window, 0 otherwise.
    Features: Calculated purely on orders placed BEFORE or ON Cutoff Date.
    """
    delivered = df_ord[df_ord["order_status"] == "Delivered"].copy()
    max_date = delivered["order_date"].max()
    cutoff_date = max_date - datetime.timedelta(days=cutoff_days)

    print(f"Dataset End Date: {max_date.date()} | Churn Cutoff Date: {cutoff_date.date()}")
    print(f"Observation Window for Churn Labeling: {cutoff_date.date()} to {max_date.date()} ({cutoff_days} days)")

    # 1. Determine eligible customers: must have made at least 1 purchase BEFORE cutoff date
    hist_orders = delivered[delivered["order_date"] <= cutoff_date].copy()
    eligible_cust_ids = set(hist_orders["customer_id"].unique())

    # 2. Determine target in observation window
    future_orders = delivered[delivered["order_date"] > cutoff_date].copy()
    active_in_future = set(future_orders["customer_id"].unique())

    # Churned = 1 if NOT in active_in_future
    cust_target = []
    for cid in eligible_cust_ids:
        churned = 1 if cid not in active_in_future else 0
        cust_target.append({"customer_id": cid, "churn": churned})
    df_target = pd.DataFrame(cust_target)

    # 3. Engineer features strictly using historical orders (<= cutoff_date)
    # Join with items and products for rich behavioral signals
    hist_items = df_items.merge(hist_orders[["order_id", "customer_id", "order_date", "total_amount", "discount_amount"]], on="order_id")
    hist_items = hist_items.merge(df_prod[["product_id", "category"]], on="product_id")

    # Customer aggregates
    agg_features = hist_orders.groupby("customer_id").agg(
        first_order=("order_date", "min"),
        last_order=("order_date", "max"),
        total_orders=("order_id", "nunique"),
        total_spend=("total_amount", "sum"),
        total_discount=("discount_amount", "sum"),
        avg_order_value=("total_amount", "mean"),
        max_order_value=("total_amount", "max"),
        min_order_value=("total_amount", "min")
    ).reset_index()

    # Recency relative to cutoff date
    agg_features["recency_days"] = (cutoff_date - agg_features["last_order"]).dt.days
    agg_features["tenure_days"] = (cutoff_date - agg_features["first_order"]).dt.days
    agg_features["discount_ratio"] = (agg_features["total_discount"] / agg_features["total_spend"]).fillna(0.0).round(4)

    # Category diversity and units bought
    item_aggs = hist_items.groupby("customer_id").agg(
        unique_categories=("category", "nunique"),
        total_units_bought=("quantity", "sum"),
        avg_item_price=("unit_price", "mean")
    ).reset_index()

    # Order momentum: spend in last 60 days before cutoff vs earlier
    recent_window_start = cutoff_date - datetime.timedelta(days=60)
    recent_spend = hist_orders[hist_orders["order_date"] >= recent_window_start].groupby("customer_id")["total_amount"].sum().reset_index()
    recent_spend.rename(columns={"total_amount": "spend_last_60d"}, inplace=True)

    # Inter-purchase interval variance
    order_gaps = hist_orders.sort_values(by=["customer_id", "order_date"]).copy()
    order_gaps["prev_date"] = order_gaps.groupby("customer_id")["order_date"].shift(1)
    order_gaps["gap_days"] = (order_gaps["order_date"] - order_gaps["prev_date"]).dt.days
    gap_stats = order_gaps.groupby("customer_id")["gap_days"].agg(["mean", "std"]).reset_index()
    gap_stats.rename(columns={"mean": "avg_order_gap_days", "std": "std_order_gap_days"}, inplace=True)
    gap_stats["std_order_gap_days"] = gap_stats["std_order_gap_days"].fillna(0.0)

    # Merge all feature tables
    features = agg_features.merge(item_aggs, on="customer_id", how="left")
    features = features.merge(recent_spend, on="customer_id", how="left")
    features["spend_last_60d"] = features["spend_last_60d"].fillna(0.0)
    features["spend_momentum_ratio"] = (features["spend_last_60d"] / (features["total_spend"] + 1.0)).round(4)
    features = features.merge(gap_stats, on="customer_id", how="left")
    features["avg_order_gap_days"] = features["avg_order_gap_days"].fillna(features["recency_days"])

    # Demographics
    features = features.merge(
        df_cust[["customer_id", "age", "gender", "division", "acquisition_channel", "customer_type"]],
        on="customer_id",
        how="left"
    )

    # Merge target
    full_df = features.merge(df_target, on="customer_id", how="inner")
    
    # Feature columns to retain for ML modeling
    numeric_features = [
        "recency_days", "tenure_days", "total_orders", "total_spend", "avg_order_value",
        "max_order_value", "discount_ratio", "unique_categories", "total_units_bought",
        "avg_item_price", "spend_last_60d", "spend_momentum_ratio", "avg_order_gap_days",
        "std_order_gap_days", "age"
    ]

    # One-hot encode categorical features
    cat_df = pd.get_dummies(full_df[["gender", "division", "acquisition_channel", "customer_type"]], drop_first=True)
    
    X = pd.concat([full_df[numeric_features], cat_df], axis=1)
    y = full_df["churn"]

    print(f"Eligible Customer Records: {len(full_df):,}")
    print(f"Overall Churn Rate: {y.mean() * 100:.2f}% ({y.sum():,} churned, {(len(y) - y.sum()):,} retained)")

    return X, y, full_df


def train_and_compare_models(
    X: pd.DataFrame, 
    y: pd.Series
) -> Tuple[Dict[str, Any], Any, StandardScaler, pd.DataFrame]:
    """
    Splits data stratifying on churn, trains Logistic Regression, Random Forest, and XGBoost,
    evaluates across metrics, and selects the champion model.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Class weight adjustment for balance
    scale_pos_weight = (len(y_train) - sum(y_train)) / sum(y_train)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, class_weight="balanced", n_jobs=-1),
        "XGBoost": XGBClassifier(n_estimators=150, max_depth=5, learning_rate=0.08, scale_pos_weight=scale_pos_weight, random_state=42, eval_metric="logloss", n_jobs=-1)
    }

    results = {}

    for name, model in models.items():
        print(f"Training {name}...")
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            y_pred = (y_pred_proba >= 0.50).astype(int)
        else:
            model.fit(X_train, y_train)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            y_pred = (y_pred_proba >= 0.50).astype(int)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        pr_auc = average_precision_score(y_test, y_pred_proba)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "confusion_matrix": cm.tolist()
        }

    # Select champion model based on highest F1-score
    champion_name = max(results.keys(), key=lambda k: results[k]["f1_score"])
    best_model = models[champion_name]
    print(f"\nChampion Model Selected: {champion_name} (F1-score: {results[champion_name]['f1_score']:.4f})")

    comparison_df = pd.DataFrame(results).T
    print("\n--- MODEL PERFORMANCE COMPARISON ---")
    print(comparison_df[["accuracy", "precision", "recall", "f1_score", "roc_auc", "pr_auc"]])

    test_data = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }

    return results, best_model, scaler, test_data
