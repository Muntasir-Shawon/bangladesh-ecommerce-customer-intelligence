# Power BI Dashboard Architecture & Technical Specification

**Project:** Bangladesh E-Commerce Customer Intelligence Platform  
**Target Tool:** Microsoft Power BI Desktop / Power BI Service  
**Model Design:** Kimball Star Schema Dimensional Modeling  

---

## 1. Dimensional Data Model (Star Schema)

The Power BI reporting semantic model connects four core tables and one shared calendar dimension:

```text
                  ┌────────────────────┐
                  │      dim_date      │
                  └─────────┬──────────┘
                            │ 1
                            │
                            │ * (order_date)
┌────────────────────┐    ┌─┴──────────────────┐    ┌────────────────────┐
│   dim_customers    ├──1─┤    fact_orders     ├──1─┤    dim_products    │
└────────────────────┘  * └─────────┬──────────┘  * └─────────┬──────────┘
                                    │ 1                       │ 1
                                    │                         │
                                    │ * (order_id)            │ * (product_id)
                                  ┌─┴─────────────────────────┴─┐
                                  │      fact_order_items       │
                                  └─────────────────────────────┘
```

### Table Relationships & Cardinality
1. `dim_customers[customer_id]` 1 → `* fact_orders[customer_id]` (Single Direction)
2. `dim_date[date]` 1 → `* fact_orders[order_date]` (Single Direction)
3. `dim_products[product_id]` 1 → `* fact_order_items[product_id]` (Single Direction)
4. `fact_orders[order_id]` 1 → `* fact_order_items[order_id]` (Single Direction)

---

## 2. Dashboard Layout & Page Specifications

### PAGE 1 — EXECUTIVE OVERVIEW
**Target Audience:** C-Suite, Managing Director, Head of Operations  
**Primary Question:** What is the overarching health and trajectory of our e-commerce business in Bangladesh?

#### Top KPI Scorecard Banner
1. **Total Revenue:** `436.66M BDT` (Card Visual | MoM Indicator: `+4.2% ▲`)
2. **Total Orders:** `70,936` (Card Visual | Delivered status filter applied)
3. **Active Customers:** `33,389` (Card Visual)
4. **Average Order Value (AOV):** `6,155.67 BDT` (Card Visual)
5. **Gross Profit Margin:** `34.71%` (Card Visual)
6. **Repeat Purchase Rate:** `52.8%` (Card Visual)
7. **Customer Churn Rate:** `87.9%` (Card Visual | 90-day inactivity)

#### Core Analytical Visuals
- **Visual 1 (Area / Line Chart):** Monthly Gross Revenue & Gross Profit Trajectory (Jan 2023 - Sep 2025) with Eid retail peak annotations.
- **Visual 2 (Clustered Bar Chart):** Revenue Contribution by Product Category (`Fashion`, `Electronics`, `Beauty`, etc.).
- **Visual 3 (Filled Map / Treemap):** Revenue Distribution across Bangladesh Administrative Divisions (Dhaka 54%, Chattogram 16%, Sylhet 7%, etc.).
- **Visual 4 (Donut Chart):** Payment Method Breakdown (`bKash`, `Cash on Delivery`, `Nagad`, `Card`, `Bank Transfer`).
- **Visual 5 (Table Visual):** Top 10 Best-Selling Products by Net Realized Revenue.

#### Global Slicers (Top Ribbon)
- Date Range Slider (`2023-01-01` to `2025-09-30`)
- Administrative Division Dropdown
- Customer Type (`Individual` vs `Corporate / SME`)
- Acquisition Channel Multi-Select

---

### PAGE 2 — CUSTOMER INTELLIGENCE & SEGMENTATION
**Target Audience:** Head of CRM, Retention Marketing Lead, Growth Strategist  
**Primary Question:** Who are our most valuable customer segments, and how do their behaviors differ?

#### Top KPI Scorecard Banner
1. **Champions Revenue Share:** `34.8%` (from only 16.0% of customers)
2. **Average Spend per Champion:** `28,458.90 BDT`
3. **Average Order Frequency (Champions):** `4.6 Orders`
4. **At-Risk Customer Count:** `6,372`

#### Core Analytical Visuals
- **Visual 1 (Dual-Axis Bar & Line Chart):** RFM Segment Distribution: % of Customer Base vs % of Total Revenue.
- **Visual 2 (Scatter Plot):** Customer Behavioral Clustering (Recency on X-axis, Monetary on Y-axis Log Scale, Bubble Size = Frequency).
- **Visual 3 (Matrix Visual with Drill-Down):** RFM Persona Hierarchy:
  - Level 1: RFM Segment (`Champions`, `Loyal Customers`, `At Risk`, `Hibernating`)
  - Level 2: Division & City
  - Metrics: Customer Count, Average Recency, Average Frequency, Total Spend, AOV.
- **Visual 4 (Stacked Bar Chart):** Acquisition Channel by Customer Segment (identifying which channels yield Champions).

#### Interactivity & Drill-Through
- Right-click any RFM segment bar to drill through to a granular customer roster displaying `customer_id`, `age`, `city`, `last_order_date`, and `lifetime_spend`.

---

### PAGE 3 — RETENTION & CHURN DIAGNOSTICS
**Target Audience:** Retention Marketing Manager, Customer Success Lead  
**Primary Question:** Which customers are slipping away, what drives their churn, and how do we intervene?

#### Top KPI Scorecard Banner
1. **90-Day Churn Rate:** `87.89%`
2. **High-CLV / High-Risk Customers:** `1,240` accounts requiring urgent outreach
3. **At-Risk Gross Margin:** `18.4M BDT`
4. **Average Order Gap (Active):** `43.2 Days`

#### Core Analytical Visuals
- **Visual 1 (Matrix / Custom Heatmap):** Monthly Acquisition Cohort Retention Grid ($M_0$ to $M_{12}$).
- **Visual 2 (Tornado / Horizontal Bar Chart):** SHAP Global Churn Driver Feature Importance (Recency Decay, Spend Momentum, Category Diversity).
- **Visual 3 (Histogram / Distribution):** Machine Learning Predicted Churn Probability Distribution across Customer Base.
- **Visual 4 (Action Table):** Priority Intervention Roster:
  - Columns: `customer_id`, `city`, `lifetime_orders`, `lifetime_spend`, `days_inactive`, `churn_risk_score`, `recommended_action`.
  - Conditional formatting: Churn probability > 70% highlighted in Red.

---

### PAGE 4 — PRODUCT PROFITABILITY & REVENUE OPTIMIZATION
**Target Audience:** Commercial Merchandising Director, Category Managers  
**Primary Question:** Which categories and SKUs deliver true bottom-line margin vs diluting profit?

#### Top KPI Scorecard Banner
1. **Overall Gross Product Margin:** `34.71%`
2. **Highest Margin Category:** `Mobile Accessories (54.2%)`
3. **Lowest Margin Category:** `Grocery (14.1%)`
4. **Total Promotional Discounts Given:** `14.2M BDT`

#### Core Analytical Visuals
- **Visual 1 (BCG Growth-Share Scatter Matrix):** Category Matrix (X-axis = Total Revenue BDT, Y-axis = Gross Profit Margin %, Bubble Size = Units Sold).
- **Visual 2 (Waterfall Chart):** Gross Catalog Value → Line Item Discounts → Order Vouchers → Net Realized Revenue.
- **Visual 3 (Clustered Bar Chart):** Category Delivery Outcome (Delivered % vs Returned % vs Cancelled %).
- **Visual 4 (Table Visual):** Bottom 20 Underperforming SKUs (Low volume, high return rate).

---

## 3. Prescriptive What-If Scenario Parameters

Four dynamic What-If parameter sliders configured in Power BI:
1. `What-If Repeat Frequency (+0% to +25%)`: Controls expected orders per repeat customer.
2. `What-If Churn Reduction (-0% to -15%)`: Controls saved customer retention.
3. `What-If AOV Expansion (+0% to +20%)`: Models checkout cross-selling uplift.
4. `What-If Discount Reduction (-0% to -30%)`: Models subsidy reallocation directly to EBITDA.
