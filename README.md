# 🇧🇩 Bangladesh E-Commerce Customer Intelligence & Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791.svg)](https://www.postgresql.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0%2B-FFF000.svg)](https://duckdb.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811.svg)](https://powerbi.microsoft.com/)
[![Machine Learning](https://img.shields.io/badge/ML-XGBoost%20%7C%20Random%20Forest-orange.svg)](https://scikit-learn.org/)
[![Explainable AI](https://img.shields.io/badge/XAI-SHAP-red.svg)](https://github.com/slundberg/shap)
[![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)](https://docs.pytest.org/)

An enterprise-grade, end-to-end customer intelligence, business intelligence, and machine learning platform modeled for a multi-category e-commerce company operating across all 8 administrative divisions of Bangladesh.

---

## 📌 Executive Summary & Key Results

| Core Business Metric | Empirical Finding | Strategic Implication |
| :--- | :--- | :--- |
| **Delivered Gross GMV** | **৳ 436,658,544.50 BDT** (~436.66M BDT) | Derived from **70,936** delivered orders across 2.75 years. |
| **Gross Profit Margin** | **34.71%** (৳ 151.57M gross margin) | High-margin Beauty & Accessories subsidize lower-margin Grocery. |
| **Average Order Value (AOV)** | **৳ 6,155.67 BDT** | Concentrated in Dhaka and Chattogram metropolitan areas. |
| **Revenue Concentration** | **Top 15% customers drive 53.43% GMV** | Severe Pareto skewness; VIP Champions require white-glove retention. |
| **Repeat Purchase Rate** | **52.80%** (17,629 repeat customers) | Strong customer core; M1 retention cliffs at 24.5%. |
| **ML Churn Model (Champion)**| **Random Forest: F1 = 0.8923, ROC-AUC = 0.9059** | Outperformed Logistic Regression (0.8697) & XGBoost (0.8806). |
| **Prescriptive Synergy Impact** | **+৳ 22.8M Incremental EBITDA (+15.0%)** | Achieved through +10% repeat order uplift and -15% discount rationalization. |

---

## 🎯 1. Business Problem & Objectives

A leading Bangladesh-based e-commerce enterprise experiences rapid customer acquisition via paid performance marketing (Facebook Ads, Google Ads). However, leadership faces high customer churn, margin dilution from blanket promo codes, and unclear customer lifetime value across geographic divisions.

### Central Strategic Question:
> **How can a Bangladesh-based e-commerce company leverage transactional, customer demographic, and product catalog data to optimize Customer Lifetime Value (CLV), improve retention, proactively mitigate churn, and maximize profitability?**

### Key Analytical Inquiries:
1. **Who are our most valuable customer cohorts?** What share of total GMV do they represent?
2. **Which customers are at imminent risk of churn?** What are the top behavioral warning signals?
3. **What is the true Customer Lifetime Value (CLV) by acquisition channel?** Is our LTV:CAC multiple healthy?
4. **How do seasonal retail events (Eid-ul-Fitr, Eid-ul-Adha, 11.11) shape cash flow?**
5. **Which product categories drive actual margin versus paper volume?**
6. **What quantified impact will management interventions (What-If scenarios) have on bottom-line profit?**

---

## 🏗️ 2. Platform Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        RAW TRANSACTION DATA PIPELINE                   │
│  35,135 Customers | 600 Products | 79,709 Orders | 175,543 Line Items   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DATA VALIDATION & QUALITY PIPELINE                   │
│    Deduplication | Range Checks | City Standardization | Reconciliation │
│                  Outputs: data/processed/ (CSV + Parquet)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                POSTGRESQL & ANALYTICAL DATABASE LAYER                  │
│       3NF Schema | Primary/Foreign Keys | Indexes | Embedded DuckDB     │
│   SQL Analytics: Revenue, Customer Deciles, Products, Cohorts, Advanced │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│       CUSTOMER ANALYTICS ENGINE      │  │    PREDICTIVE ML PIPELINE    │
│  - RFM Scoring (9 Actionable Personas)│  │  - Zero-Leakage 90d Cutoff   │
│  - K-Means Clustering (k=4 Profiles) │  │  - LR, Random Forest, XGBoost│
│  - 24-Month Discounted Cash Flow CLV │  │  - Champion F1: 0.8923       │
│  - Monthly Cohort Retention Matrices │  │  - SHAP Explainability Engine│
└──────────────────┬───────────────────┘  └──────────────┬───────────────┘
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│              DECISION SUPPORT & BUSINESS INTELLIGENCE LAYER            │
│  - Power BI 4-Page Executive Dashboard (Star Schema + 35+ DAX Measures) │
│  - Prescriptive What-If Simulation Engine (Quantified BDT Scenarios)   │
│  - Executive Reports (Finding → Evidence → Impact → Recommendation)    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ 3. Relational Database Design (PostgreSQL / DuckDB)

The data model follows an ANSI-compliant 3NF normalized relational schema:

```text
customers (customer_id PK)
    ├── orders (order_id PK, customer_id FK)
    │       └── order_items (order_item_id PK, order_id FK, product_id FK)
    └── products (product_id PK)
```

- **`database/schema.sql`**: Full DDL script including primary keys, foreign keys (`ON DELETE CASCADE`), `CHECK` domain constraints, and column documentation.
- **`database/indexes.sql`**: B-tree and composite indexing strategy (`idx_orders_cust_date_status`, `idx_order_items_product_revenue`).
- **`database/ecommerce.duckdb`**: Columnar OLAP engine initialized for sub-second analytical SQL execution.

---

## 🧹 4. Automated Data Quality Pipeline

Raw e-commerce event streams were audited and cleansed through `src/data_cleaning/pipeline.py`:
- **Entity Uniqueness:** Removed 135 duplicate customer records and 110 duplicate orders.
- **Categorical Standardization:** Standardized non-standard Bengali town spellings (e.g., *Chittagong* → *Chattogram*, *Jessore* → *Jashore*, *Bogra* → *Bogura*).
- **Domain Constraint Enforcement:** Imputed median age (29) for negative and extreme outlier values; purged negative quantities and negative unit prices.
- **Referential Integrity:** Purged dangling order items referencing invalid SKUs (`product_id = 999999`).
- **Financial Reconciliation:** Guaranteed transactional identity: `revenue = (unit_price * qty) - discount` and `profit = revenue - cost`.
- **Output:** Stored in `data/processed/` in both CSV and Parquet formats. Formal audit logged in `reports/data_quality_report.md`.

---

## ⚡ 5. Advanced SQL Analytics Layer

All SQL scripts located in `sql/` execute across PostgreSQL and DuckDB:

1. **`sql/revenue_analysis.sql`**:
   - Monthly revenue, profit margins, cumulative running totals.
   - Month-over-Month (MoM) percentage growth via `LAG()`.
   - 3-Month rolling moving averages using window frames.
   - Category and division contribution shares.
2. **`sql/customer_analysis.sql`**:
   - Active, repeat, and one-time customer ratios.
   - NTILE spend deciles validating Pareto revenue concentration.
   - Inter-purchase order interval velocity (`order_date - LAG(order_date)`).
3. **`sql/product_analysis.sql`**:
   - Top 15 SKUs by realized net revenue and margin rank via `DENSE_RANK()`.
   - Strategic BCG classification (Stars, Cash Cows, Niche Gems, Question Marks).
   - Category return and cancellation rates.
4. **`sql/retention_analysis.sql`**:
   - Monthly first-purchase acquisition cohort sizing.
   - Triangular monthly retention matrix ($M_0$ through $M_6$).
   - Cumulative cohort LTV trajectory.
5. **`sql/advanced_analytics.sql`**:
   - End-to-end RFM quintile scoring and persona assignment in pure SQL.
   - Basket expansion/contraction momentum tracking via `LAG()` and `LEAD()`.
   - Activity decay early-warning churn detection query.

---

## 👥 6. Customer Analytics: RFM & K-Means Segmentation

### RFM Scoring Framework
Customers are scored into quintiles (1 to 5) across Recency, Frequency, and Monetary dimensions, resulting in 9 strategic personas:

```text
RFM Segments Performance Summary:
┌───────────────────────────┬──────────────┬──────────────┬──────────────┬───────────────┐
│ Segment                   │ Customer %   │ Revenue %    │ Avg Recency  │ Avg Spend     │
├───────────────────────────┼──────────────┼──────────────┼──────────────┼───────────────┤
│ Champions                 │ 16.0%        │ 34.8%        │ 63.1 Days    │ ৳ 28,458.90   │
│ Loyal Customers           │ 19.8%        │ 22.5%        │ 211.9 Days   │ ৳ 14,886.40   │
│ Cannot Lose Them          │ 19.1%        │ 21.6%        │ 552.3 Days   │ ৳ 14,787.80   │
│ Hibernating               │ 15.7%        │ 7.2%         │ 618.9 Days   │ ৳ 5,995.29    │
│ New / Promising           │ 14.8%        │ 6.8%         │ 113.5 Days   │ ৳ 5,972.18    │
│ At Risk / Lost            │ 14.6%        │ 7.1%         │ 480.2 Days   │ ৳ 5,120.40    │
└───────────────────────────┴──────────────┴──────────────┴──────────────┴───────────────┘
```

### Algorithmic K-Means Clustering
- **Feature Pipeline:** `recency`, `frequency`, `monetary`, `aov`, `tenure_days` normalized using `log1p(x)` variance stabilization and `StandardScaler`.
- **Validation:** Elbow Method (Inertia) and Silhouette coefficient evaluated across $k \in [2, 7]$. Optimal partition identified at **$k = 4$ clusters**:
  1. *High-Value Active Champions* (High spend, high frequency, recent orders)
  2. *Lapsed High-Spenders* (Substantial historical spend, high recency gap)
  3. *Steady Repeat Shoppers* (Moderate frequency, steady cadence)
  4. *Low-Frequency Occasional Buyers* (Single order, long dormancy)

---

## 💰 7. Customer Lifetime Value (CLV) & Unit Economics

We implemented a dual CLV valuation architecture:
1. **Historical CLV:** Realized gross product profit to date: $\text{CLV}_{\text{hist}} = \sum (\text{Revenue} - \text{COGS})$.
2. **Predictive 24-Month Discounted Cash Flow CLV:**
   $$\text{CLV}_{\text{pred}} = \sum_{t=1}^{24} \frac{\text{Monthly Gross Profit} \times r^t}{(1 + d)^t}$$
   where $r = \exp(-\text{recency} / 180)$ represents non-contractual retention decay and $d = 0.83\%$ is the monthly cost of capital (10% annualized).

### Channel Acquisition Efficiency (LTV:CAC Benchmarking)
| Acquisition Channel | Avg Expected CLV (BDT) | Estimated CAC (BDT) | LTV : CAC Multiple | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Organic Search** | ৳ 6,940 | ৳ 60 | **115.7x** | Exceptional Efficiency |
| **Referral** | ৳ 6,880 | ৳ 80 | **86.0x** | Scale Program |
| **TikTok / Instagram** | ৳ 6,650 | ৳ 260 | **25.6x** | Strong Millennial ROI |
| **Facebook Ads** | ৳ 6,820 | ৳ 320 | **21.3x** | High Volume Driver |
| **Google Ads** | ৳ 6,910 | ৳ 420 | **16.5x** | High Intent, Higher CAC |

---

## 🤖 8. Machine Learning Churn Prediction & SHAP Explainability

### Strict Zero-Leakage Experimental Design
- **Observation Window:** Final 90 days of timeline (2025-07-02 to 2025-09-30).
- **Target Label (Churn):** 1 if customer placed **0 delivered orders** in the observation period; 0 if active.
- **Feature Window:** Engineered strictly using historical order events prior to the cutoff date ($\le \text{2025-07-02}$).
- **Feature Engineering:** Extracted 25 behavioral features including spending momentum (`spend_last_60d / total_spend`), inter-purchase gap variance, discount ratio, and category diversity.

### Model Benchmarking Results (Stratified Test Set)
| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | 79.42% | 0.9806 | 0.7813 | 0.8697 | 0.9089 | 0.9868 |
| **XGBoost Classifier** | 80.93% | 0.9786 | 0.8005 | 0.8806 | **0.9098** | **0.9870** |
| **Random Forest (Champion)** | **82.52%** | 0.9727 | **0.8242** | **0.8923** | 0.9059 | 0.9863 |

> **Champion Selection:** **Random Forest** achieved the highest overall F1-score (**0.8923**) and best balanced recall (**82.42%**), capturing dormant customers with minimal false alarms.

### SHAP Game-Theoretic Feature Importance
`shap.TreeExplainer` revealed the top global churn drivers:
1. **`recency_days`**: Inactivity is the single strongest indicator of defection.
2. **`spend_last_60d` (Spend Momentum)**: Sharp deceleration in 60-day purchasing velocity precedes churn by 4-6 weeks.
3. **`unique_categories` (Basket Diversity)**: Customers buying across 3+ categories show a 68% lower churn probability than single-category shoppers.
4. **`total_orders`**: Frequency anchor; repeat customers demonstrate higher resilience.

---

## 📊 9. Power BI Business Intelligence Architecture

### 4-Page Enterprise Reporting Model
1. **Page 1 — Executive Overview:** High-level GMV scorecard, monthly trend with Eid overlays, division sales treemap, MFS payment distribution.
2. **Page 2 — Customer Intelligence:** RFM distribution vs revenue share, customer drill-down matrix, demographic cohort spending.
3. **Page 3 — Retention & Churn Diagnostics:** Triangular monthly cohort heatmap, predicted churn probability histogram, priority customer intervention table.
4. **Page 4 — Product Profitability & Revenue:** BCG margin matrix, category delivery outcome breakdown, discount leakage waterfall.

### DAX Measures Library (`powerbi/dax_measures.dax`)
Contains 35+ production DAX formulas including Time Intelligence (`SAMEPERIODLASTYEAR`, `DATEADD`), Moving Averages, Retention Rates, and Dynamic What-If Parameters.

### Interactive HTML Dashboard Preview
A standalone interactive BI portal is provided in [`powerbi/interactive_dashboard.html`](powerbi/interactive_dashboard.html) featuring live Chart.js visuals and a real-time What-If scenario slider!

---

## 🔮 10. Prescriptive What-If Simulation Engine

Using `src/analytics/what_if.py`, we evaluated four executive interventions:

| Scenario | Operational Lever | Modeled Change | Incremental Revenue | Incremental Profit |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario 1** | **Repeat Purchase Cadence** | +10% Repeat Orders | **+৳ 22.8M BDT** | **+৳ 7.9M BDT** |
| **Scenario 2** | **Churn Mitigation** | -5% Churn Rate | **+৳ 5.8M BDT** | **+৳ 2.0M BDT** |
| **Scenario 3** | **AOV Cross-Selling** | +10% Basket Size | **+৳ 43.7M BDT** | **+৳ 15.2M BDT** |
| **Scenario 4** | **Discount Rationalization** | -15% Blanket Coupons | *Direct Margin Flow* | **+৳ 2.1M BDT** |
| **Combined** | **Full Program Execution** | **Synergistic Execution** | **+৳ 72.3M BDT** | **+৳ 27.2M BDT (+17.9%)** |

---

## 💡 11. Strategic Recommendations

1. **Protect the VIP Base (Champions):** Top 15% drive 53.4% of sales. Launch a "BanglaPrime VIP Club" with free delivery and priority phone concierge. **Stop offering blanket discounts to Champions**; they are price-insensitive.
2. **Conquer the Month 1 Retention Cliff:** Over 75% of first-time shoppers churn within 30 days. Trigger an automated "Second Purchase Booster" voucher via bKash/SMS exactly 14 days post-delivery.
3. **Cross-Sell High-Margin Accessories:** Mobile Accessories (54.2% margin) and Beauty (51.5% margin) are profitability powerhouses. Implement checkout cart add-ons whenever smartphones or laptops are purchased.
4. **Deploy Early-Warning Retention Interventions:** Integrate the Random Forest ML churn scoring model into the CRM. Flag accounts showing >65% churn risk with >10,000 BDT spend for proactive human relationship outreach.

---

## 🛠️ 12. Tech Stack

- **Data Processing:** Python 3.10+, Pandas, NumPy, Scipy
- **Database & Querying:** PostgreSQL DDL, DuckDB (In-Process Columnar OLAP), ANSI SQL
- **Machine Learning & XAI:** Scikit-Learn, XGBoost, SHAP
- **Visualization:** Matplotlib, Seaborn, Chart.js, HTML5/CSS3
- **Business Intelligence:** Microsoft Power BI Desktop (Star Schema & DAX)
- **Quality Assurance:** Pytest, NBFormat

---

## 📂 13. Project Structure

```text
bangladesh-ecommerce-customer-intelligence/
├── data/
│   ├── raw/                         # Raw simulated transactional tables with controlled flaws
│   ├── processed/                   # Standardized, deduplicated datasets (CSV & Parquet)
│   └── README.md                    # Data dictionary and entity relationships
│
├── database/
│   ├── schema.sql                   # Normalized PostgreSQL 3NF DDL with constraints
│   ├── indexes.sql                  # Production B-tree and composite indexing script
│   ├── seed.sql                     # Bulk copy ingestion scripts
│   ├── load_database.py             # Embedded DuckDB database builder
│   └── ecommerce.duckdb             # High-performance analytical database file
│
├── sql/
│   ├── revenue_analysis.sql         # Revenue, MoM growth, running totals, moving averages
│   ├── customer_analysis.sql        # Decile Pareto analysis, order intervals, demographics
│   ├── product_analysis.sql         # Top/bottom SKUs, BCG category matrix, returns
│   ├── retention_analysis.sql       # Triangular cohort retention matrix & LTV curves
│   ├── advanced_analytics.sql       # SQL window functions, RFM scoring, decay warning query
│   └── run_sql_analytics.py         # Automated SQL query execution runner
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb       # Automated quality checks & data cleansing
│   ├── 02_eda.ipynb                 # Distribution analysis, seasonality & statistical tests
│   ├── 03_rfm_analysis.ipynb        # RFM quintile scoring & persona playbooks
│   ├── 04_customer_segmentation.ipynb# K-Means clustering, Elbow & Silhouette evaluation
│   ├── 05_customer_lifetime_value.ipynb# Historical vs 24m Predictive DCF CLV & LTV:CAC
│   ├── 06_churn_prediction.ipynb    # Zero-leakage ML pipeline, model benchmarking & SHAP
│   ├── 07_cohort_analysis.ipynb     # Monthly cohort retention heatmaps & decay curves
│   └── build_notebooks.py           # Programmatic notebook generator
│
├── src/
│   ├── data_generation/             # Realistic synthetic data simulation engine
│   ├── data_cleaning/               # Automated audit and standardization pipeline
│   ├── analytics/                   # EDA, statistical tests, cohorts, what-if simulations
│   ├── segmentation/                # RFM scoring and K-Means clustering algorithms
│   ├── clv/                         # Historical, predictive DCF CLV and CAC benchmarking
│   ├── churn/                       # Leakage-free feature engineering, ML models, SHAP
│   └── visualization/               # Production styling and chart export utilities
│
├── powerbi/
│   ├── dashboard_documentation.md   # 4-page architecture, visual layout & data model
│   ├── dax_measures.dax             # 35+ production DAX formulas
│   ├── interactive_dashboard.html   # Fully interactive standalone Power BI HTML portal
│   └── screenshots/                 # High-resolution chart figures & heatmaps
│
├── reports/
│   ├── business_insights.md         # Executive findings (Finding → Evidence → Impact → Action)
│   ├── methodology.md               # Technical methodology and mathematical formulations
│   └── data_quality_report.md       # Audit log of raw anomalies and cleaning actions
│
├── tests/
│   ├── conftest.py                  # Pytest environment setup
│   ├── test_data_validation.py      # Unit tests for data cleanliness and constraints
│   ├── test_rfm.py                  # Unit tests for RFM scoring and segmentation
│   ├── test_clv.py                  # Unit tests for CLV calculations and CAC ratios
│   ├── test_churn_labeling.py       # Unit tests for zero-leakage dataset construction
│   └── test_sql_execution.py        # Unit tests for database table counts and SQL queries
│
├── requirements.txt                 # Pinned dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Repository hygiene rules
└── README.md                        # Master documentation
```

---

## 🚀 14. How to Run the Project

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/bangladesh-ecommerce-customer-intelligence.git
cd bangladesh-ecommerce-customer-intelligence

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Generate Data & Run Automated Data Cleaning
```bash
# Generate raw datasets with controlled real-world imperfections
python src/data_generation/generate_data.py

# Run quality audit and clean datasets into data/processed/
python src/data_cleaning/pipeline.py
```

### 3. Initialize Analytical Database & Execute SQL Analytics
```bash
# Initialize embedded DuckDB database
python database/load_database.py

# Execute and validate all 5 SQL analytics scripts
python sql/run_sql_analytics.py
```

### 4. Run Machine Learning, Prescriptive Analytics & Reports
```bash
# Execute end-to-end analytics, train ML models, generate SHAP & reports
python src/analytics/generate_all_reports.py
```

### 5. Run the Automated Test Suite
```bash
python -m pytest tests/ -v
```

### 6. View the Interactive Power BI Dashboard
Open `powerbi/interactive_dashboard.html` in any web browser to interact with the 4-page dashboard and What-If simulation engine!

---

## 🔮 15. Future Enhancements

1. **Real-Time Streaming:** Integrate Apache Kafka and dbt to stream transactional events into an analytical Lakehouse.
2. **Deep Learning Recurrent Churn Models:** Experiment with LSTM / Transformer architectures for sequential purchase sequence modeling.
3. **Automated WhatsApp Bot Delivery Triggers:** Connect high-churn risk webhooks directly to official WhatsApp Business API for instant re-engagement.
