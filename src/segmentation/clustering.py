"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: src/segmentation/clustering.py
Purpose: Unsupervised machine learning customer segmentation using K-Means,
         including feature log-transformation, StandardScaler, Elbow & Silhouette evaluation.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import Dict, Any, Tuple, List


def prepare_clustering_features(df_rfm: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, StandardScaler]:
    """
    Applies log transformation to handle high positive skewness in Monetary,
    Frequency, and AOV, followed by standard z-score normalization.
    """
    feature_cols = ["recency", "frequency", "monetary", "aov", "tenure_days"]
    df_features = df_rfm[feature_cols].copy()

    # Log1p transform to stabilize variance
    df_log = np.log1p(df_features)

    scaler = StandardScaler()
    scaled_array = scaler.fit_transform(df_log)

    return df_features, scaled_array, scaler


def evaluate_clusters(scaled_data: np.ndarray, k_range: range = range(2, 8)) -> Dict[str, List[float]]:
    """
    Calculates Inertia (Elbow Method) and Silhouette Scores across k range.
    Uses sample for silhouette score if dataset is large to ensure fast execution.
    """
    inertias = []
    silhouette_scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_data)
        inertias.append(float(kmeans.inertia_))

        # Sample 5000 rows for silhouette calculation efficiency
        sample_indices = np.random.choice(len(scaled_data), size=min(5000, len(scaled_data)), replace=False)
        sil = float(silhouette_score(scaled_data[sample_indices], kmeans.labels_[sample_indices]))
        silhouette_scores.append(sil)

    return {
        "k_values": list(k_range),
        "inertias": inertias,
        "silhouette_scores": silhouette_scores
    }


def fit_kmeans(
    df_rfm: pd.DataFrame, 
    scaled_data: np.ndarray, 
    optimal_k: int = 4
) -> Tuple[pd.DataFrame, KMeans, pd.DataFrame]:
    """
    Fits optimal K-Means model, attaches cluster labels, and generates profiles.
    """
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)

    df_clustered = df_rfm.copy()
    df_clustered["cluster"] = clusters

    # Profiling
    profiles = df_clustered.groupby("cluster").agg(
        customer_count=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_aov=("aov", "mean"),
        avg_tenure=("tenure_days", "mean")
    ).reset_index()

    total_cust = len(df_clustered)
    total_rev = df_clustered["monetary"].sum()
    cluster_rev = df_clustered.groupby("cluster")["monetary"].sum().values

    profiles["pct_customers"] = (profiles["customer_count"] / total_cust * 100).round(2)
    profiles["pct_revenue"] = (cluster_rev / total_rev * 100).round(2)

    # Business persona mapping
    persona_map = {}
    for idx, row in profiles.iterrows():
        c_id = int(row["cluster"])
        if row["avg_monetary"] > profiles["avg_monetary"].mean() and row["avg_recency"] < profiles["avg_recency"].mean():
            persona_map[c_id] = "High-Value Active Champions"
        elif row["avg_monetary"] > profiles["avg_monetary"].mean() and row["avg_recency"] >= profiles["avg_recency"].mean():
            persona_map[c_id] = "Lapsed High-Spenders"
        elif row["avg_frequency"] > 2 and row["avg_recency"] < profiles["avg_recency"].mean():
            persona_map[c_id] = "Steady Repeat Shoppers"
        else:
            persona_map[c_id] = "Low-Frequency Occasional Buyers"

    profiles["cluster_name"] = profiles["cluster"].map(persona_map)
    df_clustered["cluster_name"] = df_clustered["cluster"].map(persona_map)

    return df_clustered, kmeans, profiles
