-- ====================================================================
-- BANGLADESH E-COMMERCE CUSTOMER INTELLIGENCE PLATFORM
-- SQL Analytics: Product & Inventory Profitability Analysis
-- Dialect: ANSI SQL / PostgreSQL / DuckDB
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. Top 15 Best-Selling Products by Net Realized Revenue & Gross Margin
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.selling_price AS catalog_price_bdt,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.revenue), 2) AS total_revenue_bdt,
    ROUND(SUM(oi.profit), 2) AS total_profit_bdt,
    ROUND(SUM(oi.profit) / NULLIF(SUM(oi.revenue), 0) * 100, 2) AS profit_margin_pct,
    DENSE_RANK() OVER (ORDER BY SUM(oi.revenue) DESC) AS revenue_rank,
    DENSE_RANK() OVER (ORDER BY SUM(oi.profit) DESC) AS profit_rank
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category, p.brand, p.selling_price
ORDER BY total_revenue_bdt DESC
LIMIT 15;

-- --------------------------------------------------------------------
-- 2. Bottom 15 Products by Units Sold (Underperformers / Dead Stock)
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.selling_price,
    COALESCE(SUM(oi.quantity), 0) AS units_sold,
    COALESCE(ROUND(SUM(oi.revenue), 2), 0.0) AS total_revenue_bdt,
    COALESCE(ROUND(SUM(oi.profit), 2), 0.0) AS total_profit_bdt
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category, p.selling_price
ORDER BY units_sold ASC, total_revenue_bdt ASC
LIMIT 15;

-- --------------------------------------------------------------------
-- 3. Category & Subcategory Profit Margin Matrix (BCG-style Matrix)
-- --------------------------------------------------------------------
WITH subcat_metrics AS (
    SELECT 
        p.category,
        p.subcategory,
        COUNT(DISTINCT oi.order_id) AS distinct_orders,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.revenue), 2) AS total_revenue,
        ROUND(SUM(oi.profit), 2) AS total_profit,
        ROUND(SUM(oi.profit) / NULLIF(SUM(oi.revenue), 0) * 100, 2) AS margin_pct
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.category, p.subcategory
)
SELECT 
    category,
    subcategory,
    distinct_orders,
    units_sold,
    total_revenue,
    total_profit,
    margin_pct,
    CASE 
        WHEN total_revenue >= 1000000 AND margin_pct >= 35 THEN 'Star: High Volume, High Margin'
        WHEN total_revenue >= 1000000 AND margin_pct < 35 THEN 'Cash Cow: High Volume, Moderate Margin'
        WHEN total_revenue < 1000000 AND margin_pct >= 35 THEN 'Niche Gem: Moderate Volume, High Margin'
        ELSE 'Question Mark: Low Volume, Lower Margin'
    END AS strategic_classification
FROM subcat_metrics
ORDER BY category, total_revenue DESC;

-- --------------------------------------------------------------------
-- 4. Order Cancellation and Return Rates by Product Category
-- --------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) AS total_order_attempts,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Delivered' THEN o.order_id END) AS delivered_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) AS returned_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Cancelled' THEN o.order_id END) AS cancelled_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT o.order_id), 0) * 100, 
        2
    ) AS return_rate_pct,
    ROUND(
        COUNT(DISTINCT CASE WHEN o.order_status = 'Cancelled' THEN o.order_id END)::FLOAT / 
        NULLIF(COUNT(DISTINCT o.order_id), 0) * 100, 
        2
    ) AS cancellation_rate_pct
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;
