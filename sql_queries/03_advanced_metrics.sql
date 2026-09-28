-- 03_advanced_metrics.sql
-- Advanced queries using CTEs and Window Functions

-- 1. Identifying Late Deliveries and their Impact on Reviews (CTE)
WITH DeliveryStatus AS (
    SELECT 
        o.order_id,
        CASE 
            WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 'Late' 
            ELSE 'On-Time' 
        END AS delivery_status
    FROM orders o
    WHERE o.order_status = 'delivered'
)
SELECT 
    ds.delivery_status,
    AVG(r.review_score) AS avg_score,
    COUNT(r.review_id) AS number_of_orders
FROM DeliveryStatus ds
JOIN order_reviews r ON ds.order_id = r.order_id
GROUP BY 1;

-- 2. Top Selling Product Category per State (Window Function)
WITH CategorySalesByState AS (
    SELECT 
        c.customer_state,
        p.product_category_name,
        SUM(oi.price) as total_sales,
        RANK() OVER(PARTITION BY c.customer_state ORDER BY SUM(oi.price) DESC) as rank
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY 1, 2
)
SELECT customer_state, product_category_name, total_sales
FROM CategorySalesByState
WHERE rank = 1;

-- 3. Customer Retention / Repeat Purchase Rate (CTE & Window Function)
WITH CustomerPurchases AS (
    SELECT 
        customer_unique_id,
        MIN(order_purchase_timestamp) AS first_purchase,
        COUNT(order_id) AS total_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY 1
)
SELECT 
    EXTRACT(MONTH FROM first_purchase) AS cohort_month,
    COUNT(customer_unique_id) AS total_customers,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_unique_id), 2) AS repeat_rate_percentage
FROM CustomerPurchases
GROUP BY 1
ORDER BY 1;
