import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "olist.db"

TABLES = {
    "olist_orders_dataset.csv":                "orders",
    "olist_order_items_dataset.csv":           "order_items",
    "olist_order_payments_dataset.csv":        "order_payments",
    "olist_order_reviews_dataset.csv":         "order_reviews",
    "olist_products_dataset.csv":              "products",
    "olist_sellers_dataset.csv":               "sellers",
    "olist_customers_dataset.csv":             "customers",
    "olist_geolocation_dataset.csv":           "geolocation",
    "product_category_name_translation.csv":   "category_translation",
}

DATE_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
}


def main():
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print("ERROR: No CSV files found in data/ folder.")
        return

    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    loaded = 0
    for csv_name, table_name in TABLES.items():
        csv_path = DATA_DIR / csv_name
        if not csv_path.exists():
            print(f"  SKIP  {csv_name} (not found)")
            continue

        parse_dates = DATE_COLS.get(table_name, None)
        df = pd.read_csv(csv_path, parse_dates=parse_dates)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"  OK    {table_name:<25s}  {len(df):>7,} rows")
        loaded += 1

    # Create useful indexes for query performance
    print("\nCreating indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_orders_id ON orders(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_items_seller ON order_items(seller_id)",
        "CREATE INDEX IF NOT EXISTS idx_payments_order ON order_payments(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_order ON order_reviews(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_products_id ON products(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_sellers_id ON sellers(seller_id)",
        "CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id)",
    ]
    for idx_sql in indexes:
        conn.execute(idx_sql)

    conn.commit()
    conn.close()

    print(f"\nDone. Loaded {loaded} tables into {DB_PATH}")
    print(f"Database size: {DB_PATH.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
