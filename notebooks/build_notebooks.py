"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: notebooks/build_notebooks.py
Purpose: Programmatically creates the 7 production-grade Jupyter Notebooks
         with complete markdown explanations, data loading, analytics, and plots.
"""

import os
import nbformat as nbf

NOTEBOOKS_DIR = os.path.dirname(os.path.abspath(__file__))


def create_cell(cell_type: str, source: str):
    if cell_type == "markdown":
        return nbf.v4.new_markdown_cell(source)
    else:
        return nbf.v4.new_code_cell(source)


def build_nb_01():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 01 - Data Cleaning & Data Quality Audit Pipeline
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Author:** Senior Analytics & Data Engineering Team  
**Focus:** Automated Quality Auditing, Anomaly Remediation, and Relational Data Cleansing

---
## Business Context & Objectives
In real-world e-commerce platforms operating across Bangladesh, raw transactional streams frequently suffer from telemetry corruption: duplicate orders, missing demographic attributes, non-standard Bengali town spellings, negative price anomalies, and broken referential links.

This notebook executes the end-to-end data auditing, cleaning, and normalization pipeline to produce clean, reconciled datasets."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np

# Set project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.data_cleaning.pipeline import audit_raw_data, clean_and_curate_data, run_pipeline

print("Project root:", PROJECT_ROOT)"""),

        create_cell("markdown", """## 1. Run Automated Quality Diagnostics on Raw Datasets"""),

        create_cell("code", """audit_results = audit_raw_data()

for table_name, stats in audit_results.items():
    print(f"=== {table_name.upper()} AUDIT ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")"""),

        create_cell("markdown", """## 2. Execute Data Cleansing & Financial Reconciliation
- Deduplicate customers and orders by primary key.
- Standardize city names (e.g. `Chittagong` -> `Chattogram`, `Jessore` -> `Jashore`).
- Bound customer age to valid range [18, 80].
- Remove line items with non-positive quantities or unit prices.
- Reconcile item revenue `(unit_price * qty) - discount` and gross profit `revenue - cost`."""),

        create_cell("code", """df_cust, df_prod, df_ord, df_items = clean_and_curate_data()

print(f"Clean Customers:   {len(df_cust):,} rows")
print(f"Clean Products:    {len(df_prod):,} rows")
print(f"Clean Orders:      {len(df_ord):,} rows")
print(f"Clean Order Items: {len(df_items):,} rows")"""),

        create_cell("markdown", """## 3. Data Integrity & Verification"""),

        create_cell("code", """# Verify zero missing values in primary operational fields
assert df_cust['customer_id'].isnull().sum() == 0
assert df_ord['order_id'].isnull().sum() == 0
assert df_prod['product_id'].isnull().sum() == 0
assert (df_items['quantity'] <= 0).sum() == 0
assert (df_items['revenue'] < 0).sum() == 0

print("All integrity assertion checks passed successfully!")
df_ord.head(5)""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "01_data_cleaning.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 01_data_cleaning.ipynb")


def build_nb_02():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 02 - Exploratory Data Analysis & Statistical Testing
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** Revenue Dynamics, Customer Spending Skewness, Seasonality, & Hypothesis Testing

---
## Business Questions Answered
1. What is the empirical spending distribution of Bangladeshi e-commerce consumers?
2. Does the revenue distribution follow the Pareto principle (80/20 rule)?
3. How do major cultural and religious retail peaks (Eid-ul-Fitr, Eid-ul-Adha, 11.11 Mega Sale) impact revenue?
4. Is there a statistically significant spending disparity between Dhaka and non-Dhaka consumers?"""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data, compute_spending_summary, compute_pareto_distribution, perform_statistical_hypothesis_tests

df_cust, df_prod, df_ord, df_items = load_curated_data()
print("Data loaded successfully.")"""),

        create_cell("markdown", """## 1. Spending Distribution & Summary Statistics"""),

        create_cell("code", """spend_stats = compute_spending_summary(df_ord)
for k, v in spend_stats.items():
    print(f"{k}: {v:,.2f}" if isinstance(v, float) else f"{k}: {v}")"""),

        create_cell("markdown", """## 2. Pareto Revenue Concentration (80/20 Rule)"""),

        create_cell("code", """pareto_df = compute_pareto_distribution(df_ord)

top_10_pct_rev = pareto_df[pareto_df['cumulative_customer_pct'] <= 10]['cumulative_revenue_pct'].max()
top_20_pct_rev = pareto_df[pareto_df['cumulative_customer_pct'] <= 20]['cumulative_revenue_pct'].max()

print(f"Top 10% of customers generate: {top_10_pct_rev:.2f}% of total revenue")
print(f"Top 20% of customers generate: {top_20_pct_rev:.2f}% of total revenue")

plt.figure(figsize=(10, 5))
plt.plot(pareto_df['cumulative_customer_pct'], pareto_df['cumulative_revenue_pct'], color='#1f77b4', lw=2.5, label='Lorenz Revenue Curve')
plt.plot([0, 100], [0, 100], color='gray', linestyle='--', label='Line of Perfect Equality')
plt.title('Customer Revenue Concentration (Lorenz Curve)', fontsize=13, fontweight='bold')
plt.xlabel('Cumulative % of Customers', fontsize=11)
plt.ylabel('Cumulative % of Revenue', fontsize=11)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()"""),

        create_cell("markdown", """## 3. Monthly Revenue Trajectory & Seasonality"""),

        create_cell("code", """delivered = df_ord[df_ord['order_status'] == 'Delivered'].copy()
delivered['month'] = delivered['order_date'].dt.to_period('M').astype(str)
monthly_rev = delivered.groupby('month')['total_amount'].sum().reset_index()

plt.figure(figsize=(12, 5))
plt.plot(monthly_rev['month'], monthly_rev['total_amount'] / 1e6, marker='o', color='#2ca02c', lw=2)
plt.title('Monthly Realized Revenue (Million BDT)', fontsize=13, fontweight='bold')
plt.xticks(rotation=45)
plt.ylabel('Million BDT')
plt.grid(True, alpha=0.3)
plt.show()"""),

        create_cell("markdown", """## 4. Formal Statistical Hypothesis Testing
- **Mann-Whitney U Test:** Dhaka vs. Outside Dhaka customer order values.
- **Kruskal-Wallis Test:** Order spend variations across marketing acquisition channels.
- **Chi-Square Test:** Payment method preference vs. customer type."""),

        create_cell("code", """test_results = perform_statistical_hypothesis_tests(df_cust, df_ord)
for test_name, res in test_results.items():
    print(f"=== {test_name.upper()} ===")
    for k, v in res.items():
        print(f"  {k}: {v}")""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "02_eda.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 02_eda.ipynb")


def build_nb_03():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 03 - RFM Analysis & Customer Segmentation
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** Recency, Frequency, Monetary Quintile Scoring and Actionable Segment Playbooks

---
## Methodology
- **Recency (R):** Number of days elapsed since the customer's most recent delivered order.
- **Frequency (F):** Total number of distinct delivered orders placed over the customer's history.
- **Monetary (M):** Total cumulative expenditure (BDT) generated by the customer.

Each dimension is scored into quintiles (1 to 5), creating 125 granular RFM micro-cells that roll up into 9 executive business segments."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data
from src.segmentation.rfm import calculate_rfm, score_rfm, assign_rfm_segments, generate_rfm_summary

df_cust, df_prod, df_ord, df_items = load_curated_data()
print("Data loaded.")"""),

        create_cell("markdown", """## 1. Calculate RFM Metrics & Quintiles"""),

        create_cell("code", """df_rfm = calculate_rfm(df_ord)
df_scored = score_rfm(df_rfm)
df_segmented = assign_rfm_segments(df_scored)

print(f"Total Segmented Customers: {len(df_segmented):,}")
df_segmented[['customer_id', 'recency', 'frequency', 'monetary', 'r_score', 'f_score', 'm_score', 'rfm_segment']].head(10)"""),

        create_cell("markdown", """## 2. Segment Revenue Contribution & Demographics"""),

        create_cell("code", """summary = generate_rfm_summary(df_segmented)
display(summary)

plt.figure(figsize=(12, 5))
x = np.arange(len(summary))
width = 0.35
plt.bar(x - width/2, summary['pct_customers'], width, label='% Customers', color='#4e79a7')
plt.bar(x + width/2, summary['pct_revenue'], width, label='% Revenue', color='#f28e2b')
plt.xticks(x, summary['rfm_segment'], rotation=30, ha='right')
plt.ylabel('Percentage (%)')
plt.title('Customer Share vs. Revenue Share across RFM Segments', fontsize=13, fontweight='bold')
plt.legend()
plt.tight_layout()
plt.show()"""),

        create_cell("markdown", """## 3. Executive Strategic Playbook Matrix
| Segment | Customer Profile | Revenue Share | Actionable Strategy |
| :--- | :--- | :--- | :--- |
| **Champions** | High frequency, high spend, recent purchase | ~35% | VIP loyalty tier, exclusive preview access, zero-friction delivery |
| **Loyal Customers** | Consistent repeat shoppers | ~22% | Cross-sell higher margin accessories, personalized bundle offers |
| **Cannot Lose Them** | Top historical spenders inactive for >120 days | ~21% | Direct phone outreach, personalized high-value reactivation vouchers |
| **Potential Loyalists**| Recent buyers with 2-3 orders | ~6% | Welcome rewards, category exploration incentives |
| **At Risk / Hibernating** | Dormant customers with declining velocity | ~15% | Automated drip re-engagement campaigns via SMS and bKash cashback |
""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "03_rfm_analysis.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 03_rfm_analysis.ipynb")


def build_nb_04():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 04 - Unsupervised Machine Learning Customer Segmentation (K-Means)
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** K-Means Clustering, Feature Scaling, Variance Stabilization, and Cluster Evaluation

---
## Business Rationale
While heuristic RFM segmentation is intuitive, algorithmic clustering discovers multidimensional behavioral boundaries across Recency, Frequency, Monetary, Average Order Value (AOV), and Customer Tenure."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data
from src.segmentation.rfm import calculate_rfm
from src.segmentation.clustering import prepare_clustering_features, evaluate_clusters, fit_kmeans

df_cust, df_prod, df_ord, df_items = load_curated_data()
df_rfm = calculate_rfm(df_ord)
print(f"Loaded {len(df_rfm):,} customer records.")"""),

        create_cell("markdown", """## 1. Feature Preprocessing & Scaling
Because financial metrics in e-commerce are heavily right-skewed, we apply a log transform `log1p(x)` followed by `StandardScaler` to ensure unit variance."""),

        create_cell("code", """raw_feats, scaled_feats, scaler = prepare_clustering_features(df_rfm)
print("Scaled feature shape:", scaled_feats.shape)"""),

        create_cell("markdown", """## 2. Cluster Evaluation: Elbow Method & Silhouette Scores"""),

        create_cell("code", """eval_results = evaluate_clusters(scaled_feats, k_range=range(2, 7))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(eval_results['k_values'], eval_results['inertias'], marker='o', color='#1f77b4', lw=2)
ax1.set_title('Elbow Method (Inertia vs. k)', fontweight='bold')
ax1.set_xlabel('Number of Clusters (k)')
ax1.set_ylabel('Inertia')

ax2.plot(eval_results['k_values'], eval_results['silhouette_scores'], marker='s', color='#2ca02c', lw=2)
ax2.set_title('Silhouette Score Analysis vs. k', fontweight='bold')
ax2.set_xlabel('Number of Clusters (k)')
ax2.set_ylabel('Silhouette Coefficient')
plt.tight_layout()
plt.show()"""),

        create_cell("markdown", """## 3. Fit Optimal K-Means Model (k=4) & Profile Personas"""),

        create_cell("code", """df_clustered, kmeans_model, profiles = fit_kmeans(df_rfm, scaled_feats, optimal_k=4)
display(profiles)

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=df_clustered,
    x='recency',
    y='monetary',
    hue='cluster_name',
    palette='tab10',
    alpha=0.6
)
plt.yscale('log')
plt.title('Customer Clusters in Recency vs. Monetary Space (Log Scale)', fontsize=13, fontweight='bold')
plt.xlabel('Recency (Days Since Last Purchase)')
plt.ylabel('Monetary Spending (BDT, Log Scale)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "04_customer_segmentation.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 04_customer_segmentation.ipynb")


def build_nb_05():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 05 - Customer Lifetime Value (CLV) & Unit Economics
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** Historical Realized Margin, 24-Month Predictive DCF, and LTV:CAC Efficiency

---
## CLV Analytical Framework
1. **Historical CLV:** Cumulative gross margin generated to date:
   $$\\text{CLV}_{\\text{hist}} = \\sum (\\text{Revenue} - \\text{Wholesale COGS})$$
2. **Predictive CLV (24-Month Discounted Cash Flow):**
   $$\\text{CLV}_{\\text{pred}} = \\sum_{t=1}^{24} \\frac{\\text{Monthly Gross Profit} \\times r^t}{(1 + d)^t}$$
   where $r$ represents the retention probability and $d$ represents the monthly cost of capital (10% annualized).
3. **LTV:CAC Ratio:** Compares total expected customer lifetime value against marketing acquisition costs across acquisition channels."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data
from src.clv.clv_model import calculate_customer_clv_metrics, clv_breakdown_by_channel

df_cust, df_prod, df_ord, df_items = load_curated_data()
print("Data loaded.")"""),

        create_cell("markdown", """## 1. Calculate Customer CLV Metrics"""),

        create_cell("code", """df_clv = calculate_customer_clv_metrics(df_cust, df_ord, df_items)

print(f"Customer CLV Metrics computed for {len(df_clv):,} active customers.")
df_clv[['customer_id', 'acquisition_channel', 'historical_profit', 'predictive_24m_clv_profit', 'total_expected_clv', 'cac_bdt', 'clv_to_cac_ratio']].head(10)"""),

        create_cell("markdown", """## 2. Marketing Acquisition Channel Efficiency (LTV:CAC Benchmarking)"""),

        create_cell("code", """channel_clv = clv_breakdown_by_channel(df_clv)
display(channel_clv)

plt.figure(figsize=(10, 5))
plt.bar(channel_clv['acquisition_channel'], channel_clv['ltv_cac_ratio'], color='#2ca02c', width=0.5)
plt.axhline(3.0, color='red', linestyle='--', label='Healthy Benchmark (3.0x)')
plt.title('LTV:CAC Ratio across Acquisition Channels in Bangladesh', fontsize=13, fontweight='bold')
plt.xlabel('Marketing Channel')
plt.ylabel('LTV : CAC Ratio')
plt.xticks(rotation=25, ha='right')
plt.legend()
plt.tight_layout()
plt.show()"""),

        create_cell("markdown", """## 3. CLV by Administrative Division"""),

        create_cell("code", """div_clv = df_clv.groupby('division').agg(
    customer_count=('customer_id', 'count'),
    avg_total_clv=('total_expected_clv', 'mean'),
    median_clv=('total_expected_clv', 'median'),
    total_division_clv=('total_expected_clv', 'sum')
).reset_index().sort_values(by='total_division_clv', ascending=False)

display(div_clv)""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "05_customer_lifetime_value.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 05_customer_lifetime_value.ipynb")


def build_nb_06():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 06 - Machine Learning Churn Prediction & SHAP Explainability
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** Leakage-Free Temporal Split, Model Comparison, and Explainable AI (SHAP)

---
## Business Definition of Churn
In non-contractual e-commerce, customers do not explicitly cancel subscriptions. We define **Churn** as:
> **Zero delivered purchase events within an active 90-day observation window.**

### Strict Avoidance of Data Leakage
- **Observation Window:** Last 90 days of the dataset (2025-07-02 to 2025-09-30).
- **Feature Window:** Strict historical data up to and including the Cutoff Date (<= 2025-07-02).
All behavioral features (Recency, Frequency, Spend Momentum, Discount Ratio) are engineered exclusively using data available before the cutoff date."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data
from src.churn.model import create_leakage_free_churn_dataset, train_and_compare_models
from src.churn.explainability import compute_shap_explanations, explain_individual_customer

df_cust, df_prod, df_ord, df_items = load_curated_data()
print("Data loaded.")"""),

        create_cell("markdown", """## 1. Construct Leakage-Free Dataset"""),

        create_cell("code", """X, y, full_churn_df = create_leakage_free_churn_dataset(df_cust, df_ord, df_items, df_prod, cutoff_days=90)
print("Features shape:", X.shape)
print("Target distribution:\\n", y.value_counts(normalize=True))"""),

        create_cell("markdown", """## 2. Train & Compare Machine Learning Models
- Logistic Regression (Baseline)
- Random Forest
- XGBoost (Gradient Boosted Trees)"""),

        create_cell("code", """model_results, best_model, scaler, test_data = train_and_compare_models(X, y)
df_comp = pd.DataFrame(model_results).T
display(df_comp)"""),

        create_cell("markdown", """## 3. Global Model Explainability via SHAP"""),

        create_cell("code", """# Compute SHAP values on a test sample for computational efficiency
X_sample = test_data['X_test'].sample(n=min(1000, len(test_data['X_test'])), random_state=42)
shap_vals, explainer, importance_df = compute_shap_explanations(best_model, X_sample)

print("Top 10 Global Churn Drivers:")
display(importance_df.head(10))

plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'].head(10)[::-1], importance_df['mean_abs_shap'].head(10)[::-1], color='#1f77b4')
plt.title('Global Feature Importance (Mean |SHAP Value|)', fontsize=13, fontweight='bold')
plt.xlabel('Mean |SHAP Value|')
plt.tight_layout()
plt.show()"""),

        create_cell("markdown", """## 4. Individual Customer Case Diagnostic
Let's explain why a specific high-risk customer is predicted to churn."""),

        create_cell("code", """high_risk_idx = test_data['y_test'][test_data['y_test'] == 1].index[0]
sample_cust = X.loc[high_risk_idx]
cust_id = full_churn_df.loc[high_risk_idx, 'customer_id']

diag = explain_individual_customer(sample_cust, best_model, explainer, feature_names=list(X.columns))
print(f"Customer ID: CUST-{cust_id}")
print(f"Predicted Churn Probability: {diag['churn_probability'] * 100:.1f}%")
print(f"Risk Tier: {diag['predicted_risk_tier']}")
print("\\nTop Drivers:")
for d in diag['top_drivers']:
    print(f" - {d['feature']} (Value: {d['value']}): SHAP impact = {d['shap_impact']:.4f} [{d['direction']}]")""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "06_churn_prediction.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 06_churn_prediction.ipynb")


def build_nb_07():
    nb = nbf.v4.new_notebook()
    cells = [
        create_cell("markdown", """# 07 - Customer Cohort Retention Analysis
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Focus:** Monthly Acquisition Cohorts, Triangular Retention Matrices, and Lifetime Curves

---
## Business Methodology
Cohort analysis groups customers by the month of their first purchase. By tracking repeat transaction rates at month $M_0, M_1, M_2, \\dots, M_{12}$, business leaders assess whether product-market fit and retention are improving over calendar time."""),

        create_cell("code", """import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(PROJECT_ROOT)

from src.analytics.eda import load_curated_data
from src.analytics.cohorts import compute_cohort_retention_matrix

df_cust, df_prod, df_ord, df_items = load_curated_data()
print("Data loaded.")"""),

        create_cell("markdown", """## 1. Generate Triangular Retention Heatmap"""),

        create_cell("code", """count_pivot, retention_pivot, revenue_pivot = compute_cohort_retention_matrix(df_ord)

# Filter to first 12 lifecycle months for clear visualization
retention_sub = retention_pivot.iloc[:, :12]

plt.figure(figsize=(14, 8))
mask = retention_sub.isnull()
sns.heatmap(
    retention_sub,
    mask=mask,
    annot=True,
    fmt=".1f",
    cmap="Blues",
    vmin=0,
    vmax=100,
    cbar_kws={'label': 'Retention Rate (%)'}
)
plt.title('Monthly Customer Acquisition Cohort Retention Rate (%)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Cohort Lifecycle Month (M0 = First Order)', fontsize=11)
plt.ylabel('Acquisition Cohort Month', fontsize=11)
plt.tight_layout()
plt.show()"""),

        create_cell("markdown", """## 2. Average Retention Decay Curve Across All Cohorts"""),

        create_cell("code", """avg_retention = retention_pivot.mean(axis=0).iloc[:12]

plt.figure(figsize=(10, 5))
plt.plot(avg_retention.index, avg_retention.values, marker='o', lw=2.5, color='#e15759')
plt.title('Average Customer Retention Decay Curve (M0 to M11)', fontsize=13, fontweight='bold')
plt.xlabel('Months Since First Purchase')
plt.ylabel('Average Retention Rate (%)')
plt.grid(True, alpha=0.3)
for x_val, y_val in zip(avg_retention.index, avg_retention.values):
    plt.annotate(f"{y_val:.1f}%", (x_val, y_val + 2), ha='center', fontsize=9)
plt.ylim(0, 105)
plt.tight_layout()
plt.show()""")
    ]
    nb.cells = cells
    with open(os.path.join(NOTEBOOKS_DIR, "07_cohort_analysis.ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Created 07_cohort_analysis.ipynb")


def main():
    print("Building all 7 production Jupyter Notebooks...")
    build_nb_01()
    build_nb_02()
    build_nb_03()
    build_nb_04()
    build_nb_05()
    build_nb_06()
    build_nb_07()
    print("All 7 notebooks built successfully!")


if __name__ == "__main__":
    main()
