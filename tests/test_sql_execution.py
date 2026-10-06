"""
Unit tests for database loading and analytical SQL query execution.
"""

import os
import pytest
import duckdb

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "ecommerce.duckdb")


@pytest.fixture
def db_conn():
    assert os.path.exists(DB_PATH), "Analytical database file does not exist!"
    con = duckdb.connect(DB_PATH, read_only=True)
    yield con
    con.close()


def test_database_table_counts(db_conn):
    tables = ["customers", "products", "orders", "order_items"]
    for t in tables:
        count = db_conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert count > 0, f"Table {t} should not be empty!"


def test_revenue_query(db_conn):
    query = """
    SELECT 
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM orders 
    WHERE order_status = 'Delivered';
    """
    res = db_conn.execute(query).fetchone()
    assert res[0] > 0
    assert res[1] > 10000000.0  # Revenue should be substantial


def test_window_function_execution(db_conn):
    query = """
    SELECT 
        customer_id,
        order_date,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS seq_num
    FROM orders
    LIMIT 10;
    """
    res = db_conn.execute(query).fetchall()
    assert len(res) == 10
