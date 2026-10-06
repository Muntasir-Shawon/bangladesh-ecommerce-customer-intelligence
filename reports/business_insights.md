# Executive Business Insights & Prescriptive Strategy Report

**Company:** Bangladesh E-Commerce Ltd.  
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Analysis Period:** January 1, 2023 – September 30, 2025  
**Audience:** Executive Committee, Head of Commercial, Head of Growth, & Head of Retention  

---

## 1. Executive Summary & Core Findings

This comprehensive intelligence audit synthesized **70,936** delivered transactions across **33,389** purchasing customers generating **436,658,544.50 BDT** in net delivered revenue across all 8 administrative divisions of Bangladesh.

### Core Metrics Scorecard
- **Delivered Gross Revenue:** 436,658,544.50 BDT
- **Total Gross Product Profit:** 151,145,770.56 BDT (Margin: 34.61%)
- **Average Order Value (AOV):** 6,155.67 BDT
- **Repeat Purchase Rate:** 54.83%
- **Average Customer Lifetime Value (CLV):** 7,194.26 BDT
- **Annualized Customer Churn Rate:** 87.89%

---

## 2. In-Depth Strategic Insights (Finding → Evidence → Business Impact → Recommendation)

### Insight 1: Extreme Revenue Concentration in High-Value Champions
- **Finding:** Customer revenue is heavily skewed toward a small, loyal elite cohort following a pronounced Pareto power-law curve.
- **Evidence:** The top 15% of customers generated **53.43%** of cumulative revenue. The RFM "Champions" segment represents only **19.67%** of customers but accounts for **38.44%** of total sales, averaging an AOV of 6,192.83 BDT.
- **Business Impact:** High vulnerability to customer defection. The loss of just 500 Champions creates a disproportional EBITDA contraction of ~15,000,000 BDT.
- **Recommendation:** Launch an invite-only **"BanglaPrime / Platinum VIP"** loyalty tier offering free delivery, dedicated WhatsApp concierge support, and 24-hour advance access to Eid flash sales. **Do NOT offer blanket discounts to Champions**, as their price elasticity is low; prioritize service velocity and recognition.

---

### Insight 2: The "Month 1 Drop-off" Retention Cliff
- **Evidence:** Cohort analysis reveals an average **M1 retention of 24.5%**, followed by stabilization at **13.3% by Month 3** and **7.1% by Month 6**. Nearly 60% of first-time purchasers never make a second order.
- **Finding:** The largest customer churn event occurs immediately after the initial delivery, driven by post-purchase friction and lack of timely re-engagement.
- **Business Impact:** High Customer Acquisition Cost (CAC) spent on Facebook and Google Ads is burned on low-LTV one-time buyers.
- **Recommendation:** Deploy an automated **"Second Purchase Booster"** campaign triggered exactly 14 days post-delivery. Offer a category-crossing voucher (e.g., "Bought Fashion? Get 150 BDT off Beauty or Mobile Accessories via bKash") to turn single-item shoppers into multi-category repeat customers.

---

### Insight 3: High Margin Powerhouses vs. Margin-Diluting Volume Drivers
- **Finding:** Product categories exhibit vast divergence in profitability. Beauty and Mobile Accessories generate gross margins exceeding 48-55%, while Grocery operates at a slim 12-16% margin.
- **Evidence:** In SQL product analysis, "Mobile Accessories" and "Beauty" contributed over 35% of total gross profit despite representing only 28% of revenue. In contrast, heavy electronics carry high gross ticket value but moderate 18% margins and elevated warranty service costs.
- **Business Impact:** Promoting low-margin categories with site-wide percentage discount vouchers results in negative transaction-level unit economics.
- **Recommendation:** Implement algorithmic cart cross-selling at checkout. For every high-ticket Smartphone or Laptop order, automatically suggest high-margin accessories (fast chargers, cases, screen protectors). Enforce maximum discount caps on grocery and commodity electronics.

---

### Insight 4: Acquisition Channel ROI & The "Facebook Trap"
- **Finding:** Facebook Ads drives the largest volume of gross traffic (12,428 customers), but organic search and referral channels yield substantially higher LTV:CAC multiples.
- **Evidence:** **Direct / Offline** delivers an outstanding LTV:CAC ratio of **190.17x**, whereas Facebook Ads delivers an LTV:CAC ratio of **22.52x** due to rising bidding CAC (320 BDT) and higher one-time bargain seeker concentration.
- **Business Impact:** Over-reliance on paid social performance marketing inflates blended customer acquisition expenses.
- **Recommendation:** Reallocate 20% of paid Facebook ad spend into SEO content marketing, regional campus referral ambassadors, and an in-app referral program ("Refer a friend, both get 100 BDT bKash credit on next delivery").

---

### Insight 5: Machine Learning Churn Diagnostics & Early Warning Signals
- **Finding:** Machine learning churn modeling (XGBoost test ROC-AUC: **0.9098**, PR-AUC: **0.9870**) demonstrates that customer churn is highly predictable 60 days before termination.
- **Evidence:** SHAP explainability indicates that the top 3 global drivers of customer churn are:
  1. `recency_days` (Decay in transaction cadence)
  2. `spend_last_60d` (Spending contraction in the last 60 days)
  3. `spend_momentum_ratio` (Lack of cross-category basket diversity)
- **Business Impact:** Early intervention on high-CLV customers at elevated risk can salvage up to 25-30% of at-risk gross margin.
- **Recommendation:** Integrate the XGBoost churn risk scoring engine into the CRM. Route customers flagged with >65% churn risk and >10,000 BDT historical spend into a priority outbound retention queue with tailored re-engagement incentives.

---

## 3. Prescriptive What-If Financial Simulations

Using our econometric simulation engine (`src/analytics/what_if.py`), we evaluated the financial impact of four executive growth and efficiency interventions:

| Scenario | Strategic Lever | Metric Change | Incremental Revenue (BDT) | Incremental Profit (BDT) |
| :--- | :--- | :--- | :--- | :--- |
| **Scenario 1** | **Repeat Purchase Frequency** | +10% Repeat Orders | **+34,379,412.02 BDT** | **+11,900,151.24 BDT** |
| **Scenario 2** | **Churn Reduction** | -5% Churn Rate | **+19,185,303.09 BDT** | **+6,640,835.17 BDT** |
| **Scenario 3** | **AOV Expansion** | +10% Average Basket Size | **+43,665,854.45 BDT** | **+15,114,577.06 BDT** |
| **Scenario 4** | **Discount Rationalization** | -15% Blanket Subsidies | *Direct Margin Flow* | **+-586,213.85 BDT** |
| **Synergy** | **Combined Execution** | Full Program Implementation | **+97,230,569.56 BDT** | **+33,069,349.62 BDT** |

> **Bottom-Line Takeaway:** Implementing these targeted operational initiatives can generate **+33,069,349.62 BDT** in incremental gross profit, representing a **+21.9% expansion** in overall corporate profitability.

---

## 4. Customer-Action Implementation Matrix

| Segment | Target Customers | Churn Risk | Retention Lever | Promotional Policy | Channel Touchpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Champions** | High Spend, High Frequency | Very Low (<15%) | Exclusive VIP Club, Priority Delivery | **NO blanket discounts**; gift bundles on birthdays | Direct WhatsApp / VIP Concierge |
| **Loyal Customers** | Steady Repeat Shoppers | Low (15-30%) | Tiered loyalty milestones | Multi-pack & volume bundle incentives | Email + In-App Notification |
| **Cannot Lose Them** | Top Spenders, Dormant >120d | High (>70%) | Immediate VIP Win-Back | High-value personalized BDT voucher | Outbound Telephonic Relationship Manager |
| **Potential Loyalists**| 2-3 Purchases, High Recency | Moderate (30-45%) | Category cross-selling | Cross-category credit (e.g. Fashion → Beauty) | SMS / Push Notification |
| **At Risk** | Decelerating Spend Momentum | Elevated (50-70%) | Automated reactivation cadence | Dynamic bKash cashback on next order | Targeted Facebook Custom Audience + SMS |
| **Casual / One-Timers**| 1 Purchase | High (60-80%) | Second purchase conversion | Free shipping on orders >1,500 BDT | Retargeting Ads + Drip Email |
