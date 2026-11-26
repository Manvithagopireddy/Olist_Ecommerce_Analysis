"""Build a validated SQLite snapshot from locally downloaded Olist CSVs."""
import argparse
import csv
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

TABLES = {
    "orders": ("olist_orders_dataset.csv", ("order_id",), ("customer_id", "order_status", "order_purchase_timestamp")),
    "order_items": ("olist_order_items_dataset.csv", ("order_id", "order_item_id"), ("product_id", "seller_id", "price", "freight_value")),
    "order_payments": ("olist_order_payments_dataset.csv", ("order_id", "payment_sequential"), ("payment_value",)),
    "order_reviews": ("olist_order_reviews_dataset.csv", (), ("review_id", "order_id", "review_score")),
    "customers": ("olist_customers_dataset.csv", ("customer_id",), ("customer_unique_id",)),
    "products": ("olist_products_dataset.csv", ("product_id",), ("product_category_name",)),
    "sellers": ("olist_sellers_dataset.csv", ("seller_id",), ()),
    "geolocation": ("olist_geolocation_dataset.csv", (), ("geolocation_zip_code_prefix",)),
    "category_translation": ("product_category_name_translation.csv", ("product_category_name",), ("product_category_name_english",)),
}
RELATIONS = [
    ("orders", "customer_id", "customers", "customer_id"),
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("order_items", "seller_id", "sellers", "seller_id"),
    ("order_payments", "order_id", "orders", "order_id"),
    ("order_reviews", "order_id", "orders", "order_id"),
]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def build(data_dir, output):
    import pandas as pd
    data_dir, output = Path(data_dir), Path(output)
    missing = [name for name, _, _ in TABLES.values() if not (data_dir / name).is_file()]
    if missing:
        raise ValueError("Missing CSVs: " + ", ".join(missing))
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {}
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        staged = Path(tmp) / "olist.db"
        conn = sqlite3.connect(staged)
        try:
            for table, (name, keys, required) in TABLES.items():
                path = data_dir / name
                checksum = digest(path)
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    header = next(csv.reader(stream), [])
                if len(header) != len(set(header)):
                    raise ValueError(f"{name}: duplicate columns")
                df = pd.read_csv(path, dtype={key: "string" for key in set(keys + required) if key.endswith("_id") or key == "customer_unique_id"})
                absent = set(keys + required) - set(df.columns)
                if absent or df.empty:
                    raise ValueError(f"{name}: missing columns {absent} or empty table")
                if keys:
                    cols = list(keys)
                    if df[cols].isna().any().any() or df.duplicated(cols).any():
                        raise ValueError(f"{name}: null or duplicate primary keys")
                for col in ("price", "freight_value", "payment_value"):
                    if col in df.columns:
                        values = pd.to_numeric(df[col], errors="raise")
                        if values.isna().any() or (~values.map(__import__("math").isfinite)).any() or (values < 0).any():
                            raise ValueError(f"{name}: invalid {col}")
                if table == "order_reviews":
                    if not df["review_score"].isin([1, 2, 3, 4, 5]).all():
                        raise ValueError("Invalid review score")
                df.to_sql(table, conn, index=False)
                if keys:
                    conn.execute(f"CREATE UNIQUE INDEX pk_{table} ON {table} ({', '.join(keys)})")
                if digest(path) != checksum:
                    raise ValueError(f"{name}: file changed during ingestion")
                manifest[table] = {"file": name, "rows": len(df), "sha256": checksum}
            for child, field, parent, key in RELATIONS:
                count = conn.execute(f"SELECT COUNT(*) FROM {child} c LEFT JOIN {parent} p ON c.{field}=p.{key} WHERE p.{key} IS NULL").fetchone()[0]
                if count:
                    raise ValueError(f"{child}.{field}: {count} orphan or null references")
                conn.execute(f"CREATE INDEX IF NOT EXISTS ix_{child}_{field} ON {child} ({field})")
            conn.execute("CREATE TABLE ingestion_manifest (table_name TEXT PRIMARY KEY, metadata TEXT NOT NULL)")
            conn.executemany("INSERT INTO ingestion_manifest VALUES (?, ?)", [(k, json.dumps(v, sort_keys=True)) for k, v in manifest.items()])
            conn.commit()
        finally:
            conn.close()
        staged.replace(output)
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("data/olist.db"))
    args = parser.parse_args()
    print(json.dumps(build(args.data_dir, args.output), indent=2))
