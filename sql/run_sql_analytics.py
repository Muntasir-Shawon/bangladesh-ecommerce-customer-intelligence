"""
Bangladesh E-Commerce Customer Intelligence Platform
Module: sql/run_sql_analytics.py
Purpose: Executes all analytical SQL files against the local database,
         validating syntax, execution speed, and printing query outputs.
"""

import os
import time
import duckdb
from tabulate import tabulate

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "ecommerce.duckdb")
SQL_DIR = os.path.join(PROJECT_ROOT, "sql")

SQL_FILES = [
    "revenue_analysis.sql",
    "customer_analysis.sql",
    "product_analysis.sql",
    "retention_analysis.sql",
    "advanced_analytics.sql"
]


def execute_sql_file(con: duckdb.DuckDBPyConnection, file_name: str):
    file_path = os.path.join(SQL_DIR, file_name)
    print(f"\n=======================================================")
    print(f"EXECUTING: {file_name}")
    print(f"=======================================================")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by semicolon into individual queries
    # Handle comments and empty statements
    raw_queries = [q.strip() for q in content.split(";") if q.strip()]

    for idx, query in enumerate(raw_queries, 1):
        # Extract query description if available in comments
        lines = query.splitlines()
        desc = "Query " + str(idx)
        for line in lines:
            if line.startswith("--") and any(k in line for k in ["1.", "2.", "3.", "4.", "5."]):
                desc = line.replace("--", "").strip()
                break

        print(f"\n>>> [{file_name}] {desc}")
        start_t = time.time()
        try:
            res = con.execute(query).fetchdf()
            elapsed = time.time() - start_t
            print(f"Status: SUCCESS ({elapsed:.3f}s) | Returned {len(res)} rows")
            # Print preview of first 5 rows
            if not res.empty:
                print(tabulate(res.head(5), headers="keys", tablefmt="psql", showindex=False))
        except Exception as e:
            print(f"Status: ERROR: {e}")
            raise e


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run database/load_database.py first.")

    con = duckdb.connect(DB_PATH, read_only=True)

    total_start = time.time()
    for sql_file in SQL_FILES:
        execute_sql_file(con, sql_file)

    con.close()
    print(f"\n=======================================================")
    print(f"ALL SQL ANALYTICS EXECUTED SUCCESSFULLY IN {time.time() - total_start:.2f}s!")
    print(f"=======================================================")


if __name__ == "__main__":
    main()
