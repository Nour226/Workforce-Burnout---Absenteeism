#!/usr/bin/env bash
# run_all.sh | generate data -> create DB objects -> load -> data-quality report -> verify KPIs
#
# Usage:   ./run_all.sh [path/to/WA_Fn-UseC_-HR-Employee-Attrition.csv]
# Needs:   PostgreSQL 14+ running, the standard PG* variables set (PGHOST, PGPORT, PGUSER,
#          PGPASSWORD, PGDATABASE), and  pip install pandas numpy "psycopg[binary]"
set -euo pipefail
cd "$(dirname "$0")"

IBM_ARG=()
if [[ $# -ge 1 ]]; then IBM_ARG=(--ibm "$1"); fi

python3 scripts/generate_data.py "${IBM_ARG[@]}"
python3 scripts/load_data.py
psql -v ON_ERROR_STOP=1 -f sql/03_quality_checks.sql
python3 scripts/verify_kpis.py
