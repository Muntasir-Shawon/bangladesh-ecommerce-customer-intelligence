-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- SQL Analytics: Customer Analysis & Spending Behavior
-- Dialect: ANSI SQL / PostgreSQL / DuckDB
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. High-Level Customer Health, Repeat Rate & Frequency Overview
-- --------------------------------------------------------------------
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS lifetime_orders,
        ROUND(SUM(o.total_amount), 2) AS lifetime_spend
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'Delivered'
    GROUP BY c.customer_id
)
SELECT 
    COUNT(*) AS total_registered_customers,
    COUNT(CASE WHEN lifetime_orders > 0 THEN 1 END) AS purchasing_customers,
    COUNT(CASE WHEN lifetime_orders = 1 THEN 1 END) AS one_time_buyers,
    COUNT(CASE WHEN lifetime_orders >= 2 THEN 1 END) AS repeat_buyers,
    ROUND(
        COUNT(CASE WHEN lifetime_orders >= 2 THEN 1 END)::FLOAT / 
        NULLIF(COUNT(CASE WHEN lifetime_orders > 0 THEN 1 END), 0) * 100, 
        2
    ) AS repeat_purchase_rate_pct,
    ROUND(AVG(CASE WHEN lifetime_orders > 0 THEN lifetime_orders END), 2) AS avg_orders_per_active_cust,
    ROUND(AVG(CASE WHEN lifetime_orders > 0 THEN lifetime_spend END), 2) AS avg_revenue_per_active_cust
FROM customer_orders;

-- --------------------------------------------------------------------
-- 2. Customer Spending Deciles & Pareto Revenue Concentration (80/20 Rule)
-- --------------------------------------------------------------------
WITH customer_spend AS (
    SELECT 
        c.customer_id,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.customer_id
),
ranked_customers AS (
    SELECT 
        customer_id,
        total_orders,
        total_spend,
        NTILE(10) OVER (ORDER BY total_spend DESC) AS spend_decile
    FROM customer_spend
)
SELECT 
    spend_decile,
    COUNT(*) AS customers_in_decile,
    ROUND(MIN(total_spend), 2) AS min_spend_bdt,
    ROUND(MAX(total_spend), 2) AS max_spend_bdt,
    ROUND(AVG(total_spend), 2) AS avg_spend_bdt,
    ROUND(SUM(total_spend), 2) AS decile_total_spend_bdt,
    ROUND(SUM(total_spend) / SUM(SUM(total_spend)) OVER () * 100, 2) AS decile_pct_of_total_revenue,
    ROUND(
        SUM(SUM(total_spend)) OVER (ORDER BY spend_decile) / 
        SUM(SUM(total_spend)) OVER () * 100, 
        2
    ) AS cumulative_revenue_pct
FROM ranked_customers
GROUP BY spend_decile
ORDER BY spend_decile;

-- --------------------------------------------------------------------
-- 3. Inter-Purchase Order Interval Days (Lead/Lag Velocity)
-- --------------------------------------------------------------------
WITH ordered_transactions AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
    FROM orders
    WHERE order_status = 'Delivered'
),
intervals AS (
    SELECT 
        customer_id,
        order_date - prev_order_date AS days_between_orders
    FROM ordered_transactions
    WHERE prev_order_date IS NOT NULL
)
SELECT 
    COUNT(*) AS repeat_order_events,
    ROUND(AVG(days_between_orders), 1) AS avg_days_between_orders,
    ROUND(MEDIAN(days_between_orders), 1) AS median_days_between_orders,
    MIN(days_between_orders) AS min_gap_days,
    MAX(days_between_orders) AS max_gap_days
FROM intervals;

-- --------------------------------------------------------------------
-- 4. Customer Demographics Performance (Individual vs Corporate, Age Bands)
-- --------------------------------------------------------------------
SELECT 
    c.customer_type,
    CASE 
        WHEN c.age < 25 THEN '18-24 (Gen Z)'
        WHEN c.age BETWEEN 25 AND 34 THEN '25-34 (Millennials)'
        WHEN c.age BETWEEN 35 AND 49 THEN '35-49 (Middle Age)'
        ELSE '50+ (Seniors)'
    END AS age_cohort,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS total_revenue_bdt,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value_bdt,
    ROUND(COUNT(DISTINCT o.order_id)::FLOAT / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) AS orders_per_customer
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'Delivered'
GROUP BY 
    c.customer_type,
    CASE 
        WHEN c.age < 25 THEN '18-24 (Gen Z)'
        WHEN c.age BETWEEN 25 AND 34 THEN '25-34 (Millennials)'
        WHEN c.age BETWEEN 35 AND 49 THEN '35-49 (Middle Age)'
        ELSE '50+ (Seniors)'
    END
ORDER BY c.customer_type, total_revenue_bdt DESC;
