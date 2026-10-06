"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/churn/explainability.py
Purpose: Model explainability and interpretability using SHAP (SHapley Additive exPlanations)
         for Tree-based ensemble models (Random Forest / XGBoost).
"""

import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, Tuple, List


def compute_shap_explanations(model, X_sample: pd.DataFrame) -> Tuple[np.ndarray, shap.Explainer, pd.DataFrame]:
    """
    Computes SHAP values using TreeExplainer for the champion model.
    Handles binary classification output shapes (e.g. Random Forest outputs list/array of 2 classes).
    """
    explainer = shap.TreeExplainer(model)
    raw_shap = explainer.shap_values(X_sample)

    # For binary classification (Random Forest), shap_values can be a list of [class 0, class 1]
    # or an array of shape (N, features, 2). We extract class 1 (Churn).
    if isinstance(raw_shap, list):
        shap_values = np.array(raw_shap[1])
    elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
        shap_values = raw_shap[:, :, 1]
    else:
        shap_values = np.array(raw_shap)

    # Calculate global feature importance (mean absolute SHAP value for churn class)
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    importance_df = pd.DataFrame({
        "feature": list(X_sample.columns),
        "mean_abs_shap": mean_abs_shap
    }).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)

    importance_df["relative_importance_pct"] = (
        importance_df["mean_abs_shap"] / importance_df["mean_abs_shap"].sum() * 100
    ).round(2)

    return shap_values, explainer, importance_df


def explain_individual_customer(
    customer_row: pd.Series,
    model,
    explainer: shap.Explainer,
    feature_names: List[str]
) -> Dict[str, Any]:
    """
    Generates an individual customer churn risk diagnosis explaining
    the top drivers pushing the customer toward churn or retention.
    """
    df_single = pd.DataFrame([customer_row[feature_names]])
    prob = float(model.predict_proba(df_single)[0, 1])
    raw_shap = explainer.shap_values(df_single)

    if isinstance(raw_shap, list):
        s_vals = np.array(raw_shap[1])[0]
    elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
        s_vals = raw_shap[0, :, 1]
    else:
        s_vals = np.array(raw_shap)[0]

    # Combine features and shap impact
    impacts = []
    for f_name, f_val, s_val in zip(feature_names, df_single.iloc[0], s_vals):
        impacts.append({
            "feature": f_name,
            "value": f_val,
            "shap_impact": float(s_val),
            "direction": "Risk Driver (↑ Churn)" if s_val > 0 else "Retention Anchor (↓ Churn)"
        })

    # Sort by absolute SHAP impact
    impacts.sort(key=lambda x: abs(x["shap_impact"]), reverse=True)

    return {
        "churn_probability": round(prob, 4),
        "predicted_risk_tier": "Critical Risk (>75%)" if prob >= 0.75 else (
            "Elevated Risk (50-75%)" if prob >= 0.50 else "Safe Active (<50%)"
        ),
        "top_drivers": impacts[:5]
    }
