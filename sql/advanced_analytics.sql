-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- SQL Analytics: Advanced SQL & Predictive Behavioral Queries
-- Dialect: ANSI SQL / PostgreSQL / DuckDB
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Customer RFM Scoring Engine via SQL Window Functions & NTILE Percentiles
-- --------------------------------------------------------------------
WITH customer_aggregates AS (
    SELECT 
        c.customer_id,
        c.division,
        c.acquisition_channel,
        -- Reference observation date as max order date in dataset
        MAX(o.order_date) AS last_order_date,
        (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') - MAX(o.order_date) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(o.total_amount), 2) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.customer_id, c.division, c.acquisition_channel
),
rfm_scored AS (
    SELECT 
        customer_id,
        division,
        acquisition_channel,
        recency_days,
        frequency,
        monetary,
        -- Lower recency days = higher score (5)
        6 - NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_aggregates
),
segmented_customers AS (
    SELECT 
        customer_id,
        division,
        acquisition_channel,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        (r_score * 100 + f_score * 10 + m_score) AS rfm_code,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising Customers'
            WHEN r_score = 3 AND f_score <= 2 THEN 'Potential Loyalists'
            WHEN r_score <= 2 AND f_score >= 4 THEN 'Cannot Lose Them'
            WHEN r_score <= 2 AND f_score = 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score = 2 THEN 'Hibernating'
            ELSE 'Lost Customers'
        END AS rfm_segment
    FROM rfm_scored
)
SELECT 
    rfm_segment,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*)::FLOAT / SUM(COUNT(*)) OVER () * 100, 2) AS pct_of_customers,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 2) AS avg_frequency,
    ROUND(AVG(monetary), 2) AS avg_monetary_spend_bdt,
    ROUND(SUM(monetary), 2) AS segment_total_spend_bdt,
    ROUND(SUM(monetary) / SUM(SUM(monetary)) OVER () * 100, 2) AS pct_of_total_revenue
FROM segmented_customers
GROUP BY rfm_segment
ORDER BY segment_total_spend_bdt DESC;

-- --------------------------------------------------------------------
-- 2. Customer Order Velocity & Basket Growth Trend (LAG & LEAD)
-- --------------------------------------------------------------------
WITH customer_order_seq AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        total_amount,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_sequence_num,
        LAG(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_amount,
        LEAD(total_amount, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_amount,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_date
    FROM orders
    WHERE order_status = 'Delivered'
)
SELECT 
    customer_id,
    order_id,
    order_date,
    order_sequence_num,
    total_amount AS current_order_bdt,
    prev_order_amount,
    ROUND(total_amount - prev_order_amount, 2) AS spend_change_from_last_order,
    order_date - prev_order_date AS days_since_last_order,
    CASE 
        WHEN prev_order_amount IS NULL THEN 'First Purchase'
        WHEN total_amount > prev_order_amount * 1.2 THEN 'Basket Expansion (>20%)'
        WHEN total_amount < prev_order_amount * 0.8 THEN 'Basket Contraction (>20%)'
        ELSE 'Stable Spending'
    END AS spending_momentum
FROM customer_order_seq
WHERE order_sequence_num BETWEEN 2 AND 5
LIMIT 20;

-- --------------------------------------------------------------------
-- 3. Top-Performing Product per Category via Dense Ranking & Window Partitions
-- --------------------------------------------------------------------
WITH ranked_category_products AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        p.selling_price,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.revenue), 2) AS total_revenue_bdt,
        ROUND(SUM(oi.profit), 2) AS total_profit_bdt,
        DENSE_RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.revenue) DESC) AS rank_in_category
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.category, p.product_id, p.product_name, p.selling_price
)
SELECT 
    category,
    rank_in_category,
    product_name,
    selling_price,
    units_sold,
    total_revenue_bdt,
    total_profit_bdt,
    ROUND(total_profit_bdt / NULLIF(total_revenue_bdt, 0) * 100, 2) AS margin_pct
FROM ranked_category_products
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- --------------------------------------------------------------------
-- 4. Customer Churn Early Warning Indicator Query (Activity Decay Detection)
-- --------------------------------------------------------------------
WITH customer_decay AS (
    SELECT 
        c.customer_id,
        c.division,
        COUNT(o.order_id) AS total_lifetime_orders,
        MAX(o.order_date) AS last_order_date,
        (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') - MAX(o.order_date) AS days_since_last_purchase,
        COUNT(CASE WHEN o.order_date >= (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') - 90 THEN 1 END) AS orders_last_90d,
        COUNT(CASE WHEN o.order_date BETWEEN (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') - 180 
                                         AND (SELECT MAX(order_date) FROM orders WHERE order_status = 'Delivered') - 91 THEN 1 END) AS orders_prior_90d,
        ROUND(SUM(o.total_amount), 2) AS lifetime_value_bdt
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.customer_id, c.division
)
SELECT 
    customer_id,
    division,
    total_lifetime_orders,
    days_since_last_purchase,
    orders_last_90d,
    orders_prior_90d,
    lifetime_value_bdt,
    CASE 
        WHEN days_since_last_purchase >= 120 THEN 'Definite Churn (>120d inactive)'
        WHEN orders_prior_90d >= 2 AND orders_last_90d = 0 THEN 'High Risk (Abrupt Decay)'
        WHEN orders_last_90d < orders_prior_90d THEN 'Medium Risk (Decelerating)'
        ELSE 'Healthy Active'
    END AS churn_risk_flag
FROM customer_decay
WHERE lifetime_value_bdt >= 5000
ORDER BY lifetime_value_bdt DESC, days_since_last_purchase DESC
LIMIT 25;
