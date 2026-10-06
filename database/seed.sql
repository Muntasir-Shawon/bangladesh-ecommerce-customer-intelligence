-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- Data Seeding Script for PostgreSQL (via \copy or psql)
-- ====================================================================

-- Execute these commands inside psql connected to your PostgreSQL database:
-- Replace the absolute paths below with your actual local repository paths.

-- 1. Ingest Customers
\copy customers(customer_id, signup_date, gender, age, city, division, customer_type, acquisition_channel) FROM 'data/processed/customers.csv' WITH (FORMAT csv, HEADER true);

-- 2. Ingest Products
\copy products(product_id, product_name, category, subcategory, brand, cost_price, selling_price) FROM 'data/processed/products.csv' WITH (FORMAT csv, HEADER true);

-- 3. Ingest Orders
\copy orders(order_id, customer_id, order_date, order_status, payment_method, delivery_status, shipping_fee, discount_amount, total_amount) FROM 'data/processed/orders.csv' WITH (FORMAT csv, HEADER true);

-- 4. Ingest Order Items
\copy order_items(order_item_id, order_id, product_id, quantity, unit_price, discount, cost, revenue, profit) FROM 'data/processed/order_items.csv' WITH (FORMAT csv, HEADER true);

-- Reset sequence values to max ID
SELECT setval('customers_customer_id_seq', (SELECT MAX(customer_id) FROM customers));
SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM products));
SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM orders));
SELECT setval('order_items_order_item_id_seq', (SELECT MAX(order_item_id) FROM order_items));
