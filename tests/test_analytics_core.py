import sqlite3
import unittest
from analytics_core import metrics, repeat_rate

class MetricsTest(unittest.TestCase):
    def test_order_grain(self):
        with sqlite3.connect(":memory:") as conn:
            conn.executescript("""
            CREATE TABLE customers(customer_id, customer_unique_id, customer_state);
            CREATE TABLE orders(order_id, customer_id, order_status, order_purchase_timestamp,
                order_delivered_customer_date, order_estimated_delivery_date);
            CREATE TABLE order_payments(order_id, payment_value);
            CREATE TABLE order_reviews(order_id, review_score);
            INSERT INTO customers VALUES ('a','u','SP'),('b','u','SP'),('c','v','RJ');
            INSERT INTO orders VALUES
            ('1','a','delivered','2018-01-01','2018-01-03','2018-01-02'),
            ('2','b','delivered','2018-01-05','2018-01-06','2018-01-07'),
            ('3','c','delivered','2018-01-05',NULL,NULL);
            INSERT INTO order_payments VALUES ('1',60),('1',40),('2',50),('3',30);
            INSERT INTO order_reviews VALUES ('1',1),('1',3),('2',4);
            """)
            m = metrics(conn)
            self.assertEqual(m['delivered_orders'],3)
            self.assertEqual(m['customer_payments_brl'],180)
            self.assertEqual(m['average_paid_order_brl'],60)
            self.assertEqual(m['mean_order_review'],3)
            self.assertEqual(m['late_fraction'],0.5)
            self.assertEqual(repeat_rate(conn),0.5)
