#!/usr/bin/env python3
"""
load_data.py  |  Role A
Creates the schema, bulk-loads the 4 CSV files with COPY, then creates the KPI views.

Connection: standard libpq environment variables (PGHOST, PGPORT, PGUSER, PGPASSWORD,
PGDATABASE) or --dsn "host=... dbname=... user=...".
"""
import argparse
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent.parent

LOAD_ORDER = [  # parents first
    ("departments", "dept_id, dept_name"),
    ("employees", "employee_id, full_name, dept_id, job_role, gender, age, "
                  "distance_from_home, hire_date"),
    ("weekly_workload", "workload_id, employee_id, week_start, hours_worked"),
    ("absences", "absence_id, employee_id, start_date, end_date, absence_type, reason, is_justified"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", default="")
    ap.add_argument("--data", default=str(ROOT / "data"))
    args = ap.parse_args()
    data = Path(args.data)

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute((ROOT / "sql" / "01_schema.sql").read_text())
            for table, cols in LOAD_ORDER:
                with cur.copy(f"COPY {table} ({cols}) FROM STDIN WITH (FORMAT csv, HEADER true)") as cp:
                    with open(data / f"{table}.csv", "rb") as f:
                        while chunk := f.read(1 << 16):
                            cp.write(chunk)
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table:16s} {cur.fetchone()[0]:>8,d} rows loaded")
        conn.commit()
        conn.autocommit = True
        conn.execute("ANALYZE")
    print("schema + data + KPI views ready")


if __name__ == "__main__":
    main() 
