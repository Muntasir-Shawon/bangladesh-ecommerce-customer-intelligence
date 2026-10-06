-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- Production Indexes for PostgreSQL Query Optimization
-- ====================================================================

-- 1. Customers Table Indexes
CREATE INDEX IF NOT EXISTS idx_customers_signup_date ON customers(signup_date);
CREATE INDEX IF NOT EXISTS idx_customers_division_city ON customers(division, city);
CREATE INDEX IF NOT EXISTS idx_customers_acquisition ON customers(acquisition_channel);

-- 2. Products Table Indexes
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_category_subcategory ON products(category, subcategory);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);

-- 3. Orders Table Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_method ON orders(payment_method);
-- Composite Index for Customer Temporal Queries & RFM Analytics
CREATE INDEX IF NOT EXISTS idx_orders_cust_date_status ON orders(customer_id, order_date, order_status);

-- 4. Order Items Table Indexes
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
-- Composite Index for Category Profitability & Margin Joins
CREATE INDEX IF NOT EXISTS idx_order_items_product_revenue ON order_items(product_id, revenue, profit);
