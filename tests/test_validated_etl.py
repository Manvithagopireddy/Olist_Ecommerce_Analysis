import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from python_eda.validated_etl import TABLES, build

class TestETL(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "out.db"
        for table, (name, keys, required) in TABLES.items():
            cols = keys + required
            values = {"price": 10, "freight_value": 2, "payment_value": 12,
                      "review_score": 5, "payment_sequential": 1, "order_item_id": 1}
            with (self.root / name).open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerow([values.get(c, "example") for c in cols])

    def test_valid_snapshot(self):
        result = build(self.root, self.db)
        self.assertEqual(len(result), 9)
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM ingestion_manifest").fetchone()[0], 9)

    def test_missing_file_preserves_existing_database(self):
        build(self.root, self.db)
        before = self.db.read_bytes()
        (self.root / TABLES["orders"][0]).unlink()
        with self.assertRaises(ValueError):
            build(self.root, self.db)
        self.assertEqual(before, self.db.read_bytes())

    def test_duplicate_key_rejected(self):
        path = self.root / TABLES["orders"][0]
        with path.open("a") as f:
            f.write(path.read_text().splitlines()[1] + "\n")
        with self.assertRaises(ValueError):
            build(self.root, self.db)
        self.assertFalse(self.db.exists())

if __name__ == "__main__":
    unittest.main()
