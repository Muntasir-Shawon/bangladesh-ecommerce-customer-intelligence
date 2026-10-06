# Data Quality Audit Report
**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Audit Timestamp:** 2026-10-06 23:06:22  
**Environment:** Production Data Staging  

---

## Executive Summary

The data quality pipeline executed an automated audit against all four raw relational tables. Controlled real-world anomalies were successfully identified across entity uniqueness, referential integrity, domain constraint validity, and categorical consistency.

| Entity | Raw Rows | Duplicate Keys | Missing Values Detected | Constraint / Logic Violations | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Customers** | 35,135 | 135 | City (421), Gender (526), Channel (352) | Age Outliers (45), Non-standard cities (2,148) | Cleaned & Normalized |
| **Products** | 600 | 0 | None (100% complete) | Invalid Prices: 0 | Validated |
| **Orders** | 79,709 | 110 | Discount (1,992) | Corrupted Dates: 35 | Deduplicated & Parsed |
| **Order Items** | 175,543 | 0 | None (100% complete) | Negative Qty (42), Negative Unit Price (18), Dangling Products (22) | Cleansed & Imputed |

---

## Detailed Findings & Remediation Strategy

### 1. Customers Table
- **Deduplication:** Dropped 135 duplicate records by retaining first occurrence of `customer_id`.
- **Categorical Standardization:** Standardized 2148 city records by stripping whitespace, standardizing case, and mapping legacy names (e.g., *Chittagong* → *Chattogram*, *Jessore* → *Jashore*, *Bogra* → *Bogura*).
- **Missing Value Imputation:**
  - `gender`: Imputed missing demographic values with `"Unknown"`.
  - `acquisition_channel`: Imputed missing values with `"Direct / Offline"`.
  - `city`: Imputed using mode of the customer's division.
- **Domain Constraints:** Rectified 45 invalid ages (<18 or >100) by replacing with the median customer age (29).

### 2. Orders Table
- **Deduplication:** Removed 110 duplicate order records based on `order_id`.
- **Date Parsing:** Filtered out 35 corrupted date strings (`1970-00-00`), guaranteeing strictly valid chronological timestamps.
- **Discount Imputation:** Filled 1992 missing discount amounts with `0.00 BDT`.

### 3. Order Items Table
- **Integrity Enforcement:** Removed 42 rows containing negative quantities and 18 rows with negative prices.
- **Referential Integrity:** Filtered out 22 items referencing non-existent product IDs (`product_id = 999999`).
- **Financial Reconciliation:** Recalculated `revenue = (unit_price - discount) * quantity` and `profit = revenue - cost` to guarantee arithmetic consistency across transactions.

---
*Report generated automatically by `src/data_cleaning/pipeline.py`.*
