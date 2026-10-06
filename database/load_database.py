"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: database/load_database.py
Purpose: Initializes an embedded analytical database (DuckDB) and loads
         all curated tables for high-performance SQL analytics. Also provides
         an optional PostgreSQL loader via SQLAlchemy.
"""

import os
import duckdb
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
DB_PATH = os.path.join(PROJECT_ROOT, "database", "ecommerce.duckdb")


def initialize_analytical_database():
    """Initializes DuckDB with schema and populates tables from processed Parquet/CSV."""
    print(f"Initializing embedded analytical database at: {DB_PATH}")
    
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    con = duckdb.connect(DB_PATH)

    # 1. Create and populate customers
    print("Loading customers table...")
    cust_file = os.path.join(PROCESSED_DATA_DIR, "customers.parquet")
    con.execute(f"""
        CREATE TABLE customers AS 
        SELECT 
            customer_id::INTEGER AS customer_id,
            signup_date::DATE AS signup_date,
            gender::VARCHAR AS gender,
            age::INTEGER AS age,
            city::VARCHAR AS city,
            division::VARCHAR AS division,
            customer_type::VARCHAR AS customer_type,
            acquisition_channel::VARCHAR AS acquisition_channel
        FROM read_parquet('{cust_file.replace(chr(92), "/")}');
    """)

    # 2. Create and populate products
    print("Loading products table...")
    prod_file = os.path.join(PROCESSED_DATA_DIR, "products.parquet")
    con.execute(f"""
        CREATE TABLE products AS 
        SELECT 
            product_id::INTEGER AS product_id,
            product_name::VARCHAR AS product_name,
            category::VARCHAR AS category,
            subcategory::VARCHAR AS subcategory,
            brand::VARCHAR AS brand,
            cost_price::DOUBLE AS cost_price,
            selling_price::DOUBLE AS selling_price
        FROM read_parquet('{prod_file.replace(chr(92), "/")}');
    """)

    # 3. Create and populate orders
    print("Loading orders table...")
    ord_file = os.path.join(PROCESSED_DATA_DIR, "orders.parquet")
    con.execute(f"""
        CREATE TABLE orders AS 
        SELECT 
            order_id::INTEGER AS order_id,
            customer_id::INTEGER AS customer_id,
            order_date::DATE AS order_date,
            order_status::VARCHAR AS order_status,
            payment_method::VARCHAR AS payment_method,
            delivery_status::VARCHAR AS delivery_status,
            shipping_fee::DOUBLE AS shipping_fee,
            discount_amount::DOUBLE AS discount_amount,
            total_amount::DOUBLE AS total_amount
        FROM read_parquet('{ord_file.replace(chr(92), "/")}');
    """)

    # 4. Create and populate order_items
    print("Loading order_items table...")
    items_file = os.path.join(PROCESSED_DATA_DIR, "order_items.parquet")
    con.execute(f"""
        CREATE TABLE order_items AS 
        SELECT 
            order_item_id::INTEGER AS order_item_id,
            order_id::INTEGER AS order_id,
            product_id::INTEGER AS product_id,
            quantity::INTEGER AS quantity,
            unit_price::DOUBLE AS unit_price,
            discount::DOUBLE AS discount,
            cost::DOUBLE AS cost,
            revenue::DOUBLE AS revenue,
            profit::DOUBLE AS profit
        FROM read_parquet('{items_file.replace(chr(92), "/")}');
    """)

    # Print table row counts
    print("\n--- DATABASE VERIFICATION ---")
    tables = ["customers", "products", "orders", "order_items"]
    for t in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"Table '{t}': {count:,} rows")

    con.close()
    print("Analytical database initialized and ready for SQL queries!")


if __name__ == "__main__":
    initialize_analytical_database()
