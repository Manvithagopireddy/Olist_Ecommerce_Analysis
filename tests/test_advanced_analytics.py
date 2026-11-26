import unittest
import pandas as pd
from advanced_analytics import rfm

class TestRFM(unittest.TestCase):
    def test_customer_grain_and_status(self):
        frame = pd.DataFrame([
            ("a", "1", "delivered", "2018-01-01", 10),
            ("a", "2", "delivered", "2018-08-01", 20),
            ("b", "3", "delivered", "2018-01-01", 5),
            ("c", "4", "canceled", "2018-09-01", 100),
        ], columns=["customer_unique_id", "order_id", "order_status", "order_purchase_timestamp", "payment_total"])
        result = rfm(frame)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc["a", "frequency"], 2)
        self.assertEqual(result.loc["a", "monetary"], 30)
        self.assertEqual(result.loc["a", "recency"], 1)
        self.assertEqual(result.loc["b", "segment"], "Lapsed single purchase")
