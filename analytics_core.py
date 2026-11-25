"""Canonical SQLite analytics; monetary amounts are BRL customer payments."""
import sqlite3

ORDER_FACT = """
WITH payments AS (
 SELECT order_id, SUM(payment_value) AS payment_total
 FROM order_payments GROUP BY order_id
), reviews AS (
 SELECT order_id, AVG(review_score) AS review_score
 FROM order_reviews GROUP BY order_id
)
SELECT o.order_id, c.customer_unique_id, c.customer_state,
 o.order_status, o.order_purchase_timestamp,
 p.payment_total, r.review_score,
 CASE WHEN o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN NULL
 WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END AS late
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
LEFT JOIN payments p ON p.order_id = o.order_id
LEFT JOIN reviews r ON r.order_id = o.order_id
"""

def metrics(conn: sqlite3.Connection) -> dict:
    row = conn.execute(f"""WITH fact AS ({ORDER_FACT})
    SELECT COUNT(*), COUNT(payment_total), SUM(payment_total), AVG(payment_total),
    AVG(review_score), AVG(late) FROM fact WHERE order_status='delivered'""").fetchone()
    return dict(zip(('delivered_orders','paid_orders','customer_payments_brl','average_paid_order_brl','mean_order_review','late_fraction'), row))

def repeat_rate(conn: sqlite3.Connection):
    return conn.execute(f"""WITH fact AS ({ORDER_FACT}), purchases AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS n FROM fact
    WHERE order_status='delivered' GROUP BY customer_unique_id)
    SELECT AVG(CASE WHEN n > 1 THEN 1.0 ELSE 0.0 END) FROM purchases""").fetchone()[0]
