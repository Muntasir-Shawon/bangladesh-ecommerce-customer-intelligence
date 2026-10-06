# Data Catalog & Architecture

**Platform:** Bangladesh E-Commerce Customer Intelligence Platform  
**Historical Period:** January 1, 2023 – September 30, 2025  
**Geographic Coverage:** All 8 Administrative Divisions of Bangladesh (Dhaka, Chattogram, Sylhet, Rajshahi, Khulna, Barishal, Rangpur, Mymensingh)

---

## 1. Directory Structure

```text
data/
├── raw/
│   ├── customers_raw.csv        # Raw customer signups with injected real-world flaws
│   ├── products_raw.csv         # Product catalog with cost & selling prices
│   ├── orders_raw.csv           # Raw transactions with unparsed dates & missing values
│   └── order_items_raw.csv      # Line items with negative quantities & dangling IDs
│
├── processed/
│   ├── customers.csv / .parquet     # 35,000 curated, deduplicated customers
│   ├── products.csv / .parquet      # 600 standardized products across 8 categories
│   ├── orders.csv / .parquet        # 79,547 validated orders
│   └── order_items.csv / .parquet   # 175,382 reconciled line items with accurate margins
```

---

## 2. Relational Schema & Data Dictionary

### Table: `customers` (35,000 records)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `customer_id` | INT | PRIMARY KEY | Unique customer identifier |
| `signup_date` | DATE | NOT NULL | Date account was created (2023-01 to 2025-08) |
| `gender` | VARCHAR(20) | CHECK ('Male', 'Female', 'Unknown') | Gender demographics |
| `age` | INT | CHECK (18 <= age <= 80) | Customer age in years |
| `city` | VARCHAR(50) | NOT NULL | Standardized Bangladesh city |
| `division` | VARCHAR(50) | NOT NULL | Administrative division |
| `customer_type` | VARCHAR(30) | NOT NULL | 'Individual' or 'Corporate / SME' |
| `acquisition_channel` | VARCHAR(50) | NOT NULL | Marketing channel origin (Facebook Ads, Organic, etc.) |

---

### Table: `products` (600 records)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `product_id` | INT | PRIMARY KEY | Unique product SKU identifier |
| `product_name` | VARCHAR(150) | NOT NULL | Product name including brand and specification |
| `category` | VARCHAR(50) | NOT NULL | 8 Core categories (Electronics, Fashion, Beauty, etc.) |
| `subcategory` | VARCHAR(50) | NOT NULL | Product sub-classification |
| `brand` | VARCHAR(50) | NOT NULL | Brand manufacturer |
| `cost_price` | NUMERIC(10,2) | CHECK (cost_price > 0) | Base acquisition cost in Bangladeshi Taka (BDT) |
| `selling_price` | NUMERIC(10,2) | CHECK (selling_price >= cost_price) | Retail selling price in BDT |

---

### Table: `orders` (79,547 records)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | INT | PRIMARY KEY | Unique transaction order ID |
| `customer_id` | INT | FOREIGN KEY (customers) | Purchasing customer identifier |
| `order_date` | DATE | NOT NULL | Order placement date |
| `order_status` | VARCHAR(30) | CHECK ('Delivered', 'Returned', 'Cancelled', 'Shipped', 'Processing') | Fulfillment lifecycle state |
| `payment_method` | VARCHAR(30) | CHECK ('bKash', 'Cash on Delivery', 'Nagad', 'Card', 'Bank Transfer') | Payment gateway utilized |
| `delivery_status` | VARCHAR(30) | NOT NULL | Logistics outcome |
| `shipping_fee` | NUMERIC(10,2) | DEFAULT 60.00 | Applied shipping cost in BDT |
| `discount_amount` | NUMERIC(10,2) | DEFAULT 0.00 | Order-level promotional discount applied |
| `total_amount` | NUMERIC(12,2) | CHECK (total_amount > 0) | Final billed amount in BDT |

---

### Table: `order_items` (175,382 records)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `order_item_id` | INT | PRIMARY KEY | Unique basket line item identifier |
| `order_id` | INT | FOREIGN KEY (orders) | Associated parent order ID |
| `product_id` | INT | FOREIGN KEY (products) | Purchased product ID |
| `quantity` | INT | CHECK (quantity > 0) | Units purchased |
| `unit_price` | NUMERIC(10,2) | NOT NULL | Base catalog price at moment of purchase |
| `discount` | NUMERIC(10,2) | DEFAULT 0.00 | Total discount applied to this line item |
| `cost` | NUMERIC(12,2) | NOT NULL | Total wholesale cost (`quantity * cost_price`) |
| `revenue` | NUMERIC(12,2) | NOT NULL | Net realized revenue (`(unit_price * qty) - discount`) |
| `profit` | NUMERIC(12,2) | NOT NULL | Gross profit (`revenue - cost`) |
