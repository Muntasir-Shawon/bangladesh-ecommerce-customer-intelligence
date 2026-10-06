-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- Relational Database Schema DDL (PostgreSQL Dialect)
-- ====================================================================

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- --------------------------------------------------------------------
-- 1. CUSTOMERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    signup_date DATE NOT NULL,
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Male', 'Female', 'Unknown')),
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 100),
    city VARCHAR(50) NOT NULL,
    division VARCHAR(50) NOT NULL,
    customer_type VARCHAR(30) NOT NULL DEFAULT 'Individual' CHECK (customer_type IN ('Individual', 'Corporate / SME')),
    acquisition_channel VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE customers IS 'Master customer demographic and acquisition data across Bangladesh';
COMMENT ON COLUMN customers.customer_id IS 'Unique surrogate primary key for customer';
COMMENT ON COLUMN customers.signup_date IS 'Original registration timestamp';
COMMENT ON COLUMN customers.division IS 'Administrative division (Dhaka, Chattogram, Sylhet, etc.)';
COMMENT ON COLUMN customers.acquisition_channel IS 'Marketing channel attribution (Facebook Ads, Organic, etc.)';

-- --------------------------------------------------------------------
-- 2. PRODUCTS TABLE
-- --------------------------------------------------------------------
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL CHECK (cost_price > 0),
    selling_price NUMERIC(10, 2) NOT NULL CHECK (selling_price >= cost_price),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE products IS 'Product master catalog with wholesale costs and retail prices';
COMMENT ON COLUMN products.category IS 'High-level business vertical (Electronics, Fashion, Beauty, etc.)';
COMMENT ON COLUMN products.cost_price IS 'Wholesale inventory cost in BDT';
COMMENT ON COLUMN products.selling_price IS 'Standard retail MSRP in BDT';

-- --------------------------------------------------------------------
-- 3. ORDERS TABLE
-- --------------------------------------------------------------------
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date DATE NOT NULL,
    order_status VARCHAR(30) NOT NULL CHECK (order_status IN ('Delivered', 'Returned', 'Cancelled', 'Shipped', 'Processing')),
    payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('bKash', 'Cash on Delivery', 'Nagad', 'Card', 'Bank Transfer')),
    delivery_status VARCHAR(30) NOT NULL CHECK (delivery_status IN ('Delivered', 'Returned', 'Cancelled', 'In Transit', 'Pending')),
    shipping_fee NUMERIC(10, 2) NOT NULL DEFAULT 60.00 CHECK (shipping_fee >= 0),
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount_amount >= 0),
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount > 0),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE orders IS 'Header-level order transactions';
COMMENT ON COLUMN orders.customer_id IS 'Foreign key referencing customers';
COMMENT ON COLUMN orders.payment_method IS 'MFS or traditional gateway (bKash, Nagad, COD, Card, etc.)';
COMMENT ON COLUMN orders.total_amount IS 'Final invoice amount after item discounts, shipping, and vouchers';

-- --------------------------------------------------------------------
-- 4. ORDER_ITEMS TABLE
-- --------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    discount NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0),
    cost NUMERIC(12, 2) NOT NULL CHECK (cost > 0),
    revenue NUMERIC(12, 2) NOT NULL CHECK (revenue >= 0),
    profit NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE order_items IS 'Line-item level order breakdowns with unit margins';
COMMENT ON COLUMN order_items.revenue IS 'Net realized revenue: (unit_price * quantity) - discount';
COMMENT ON COLUMN order_items.profit IS 'Realized gross margin: revenue - cost';
