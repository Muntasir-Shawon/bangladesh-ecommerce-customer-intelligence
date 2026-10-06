# Technical Methodology & Analytical Foundations

**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Architecture:** Data Generation → Automated Cleaning → PostgreSQL / DuckDB Database → Advanced SQL → Python EDA → Customer Analytics (RFM, K-Means, CLV, Cohorts) → Machine Learning (Churn & SHAP) → Power BI BI Layer  

---

## 1. Data Generation Methodology & Bangladesh Contextualization
To create an authentic simulation of the Bangladeshi e-commerce landscape:
- **Demographics:** Generated 35,000 customers distributed across all 8 administrative divisions weighted by commercial density (Dhaka: 54%, Chattogram: 16%, Sylhet: 7%, Rajshahi: 6%, Khulna: 6%, Rangpur: 4%, Barishal: 4%, Mymensingh: 3%).
- **Payment Infrastructure:** Reflects Bangladesh Bank MFS landscape (bKash: 42%, Cash on Delivery: 33%, Nagad: 15%, Cards: 8%, Bank Transfer: 2%).
- **Seasonality Engine:** Modeled religious and cultural shopping spikes:
  - Ramadan & Eid-ul-Fitr (2.2x to 2.7x baseline uplift in Fashion, Beauty, and Electronics)
  - Eid-ul-Adha (1.6x uplift in Home & Living, Grocery, and Cookware)
  - Pohela Boishakh (Bengali New Year, 1.4x uplift in Fashion and Books)
  - 11.11 Mega Campaign & Year-End Sales (2.2x uplift in Mobile Accessories and Electronics)
- **Data Quality Injections:** Introduced duplicate IDs, non-standard city casings (e.g., *Chittagong* vs *Chattogram*, *Jessore* vs *Jashore*), negative quantities/prices, missing demographic values, and corrupted dates.

---

## 2. Automated Data Quality Pipeline
The cleaning engine (`src/data_cleaning/pipeline.py`) validates datasets prior to analytical consumption:
1. **Deduplication:** Enforces primary key uniqueness on `customer_id`, `product_id`, `order_id`, and `order_item_id`.
2. **Standardization:** Normalizes categorical attributes using string sanitization and phonetic mapping dictionaries.
3. **Range Constraints:** Bounds ages to [18, 80] (imputing median 29 for outliers) and purges non-positive quantities and prices.
4. **Referential Integrity:** Verifies all order items link to existing products and orders.
5. **Reconciliation:** Recalculates `revenue = (unit_price * qty) - discount` and `profit = revenue - cost` to guarantee arithmetic consistency across transactions.

---

## 3. Database Architecture & SQL Analytics
- **Schema Design:** Implemented fully normalized Third Normal Form (3NF) relational schema in ANSI SQL / PostgreSQL dialect (`database/schema.sql`).
- **Indexing Strategy:** B-tree indexes placed on `customer_id`, `order_date`, `category`, and composite indexes on `(customer_id, order_date)` for fast temporal joins.
- **Embedded DuckDB Engine:** Utilizes an in-process, columnar OLAP database (`database/ecommerce.duckdb`) enabling instant execution of window functions (`RANK()`, `DENSE_RANK()`, `LAG()`, `LEAD()`, `NTILE()`), rolling moving averages, and cohort aggregations.

---

## 4. Customer Segmentation Frameworks
### Heuristic RFM Framework
- **Recency:** Days elapsed between customer's latest delivered order and observation date.
- **Frequency:** Total count of delivered orders.
- **Monetary:** Cumulative delivered expenditure in BDT.
- Quintiles (1-5) are calculated via rank-ordered percentile cuts (`pd.qcut`), categorizing customers into 9 actionable personas.

### Algorithmic K-Means Clustering
- Features: `recency`, `frequency`, `monetary`, `aov`, `tenure_days`.
- Preprocessing: `np.log1p` transformation to eliminate severe right-skewness, followed by `StandardScaler`.
- Validation: Evaluated across k in [2, 7] using Inertia (Elbow Method) and Silhouette Coefficients, identifying k=4 as the optimal natural cluster partition.

---

## 5. Customer Lifetime Value (CLV) Modeling
1. **Historical CLV:** Realized cumulative gross margin:
   $$\text{CLV}_{\text{hist}} = \sum (\text{Revenue} - \text{Wholesale Cost})$$
2. **Predictive CLV (24-Month Discounted Cash Flow):**
   $$\text{CLV}_{\text{pred}} = \sum_{t=1}^{24} \frac{\text{Monthly Gross Profit} \times r^t}{(1 + d)^t}$$
   where $r = \exp(-\text{recency} / 180)$ models non-contractual retention decay, and $d$ represents monthly capital cost (10% annualized).
3. **LTV:CAC Benchmarking:** Evaluates unit economics against channel acquisition costs (Facebook: 320 BDT, Google: 420 BDT, Organic: 60 BDT).

---

## 6. Churn Prediction & Model Explainability
### Zero-Leakage Experimental Setup
- **Target Observation Window:** Final 90 days of the historical timeline (2025-07-02 to 2025-09-30).
- **Feature Window:** Strictly restricted to order events prior to the cutoff date (<= 2025-07-02).
- **Churn Label:** Assigned as 1 if the customer placed 0 orders during the 90-day observation period, and 0 if active.
- **Feature Engineering:** Extracted 25 behavioral, financial, and demographic signals including spending momentum (last 60 days vs historical baseline), inter-purchase order gap variance, discount ratio, and category diversity.

### Model Benchmarking
Models evaluated using stratified train/test partitioning:
- **Logistic Regression:** Linear baseline with balanced class weights.
- **Random Forest:** Ensemble of 150 bagged decision trees.
- **XGBoost:** Gradient boosted tree ensemble with scale-pos-weight optimization.
Evaluation metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC, and PR-AUC.

### SHAP (SHapley Additive exPlanations)
Applied `shap.TreeExplainer` on the champion XGBoost model to quantify the exact game-theoretic marginal contribution of each behavioral feature toward the log-odds of customer churn.
