#!/usr/bin/env python3
"""
verify_kpis.py  |  Role A (acceptance test of the dataset)

Two kinds of checks, all run against the PostgreSQL database:
  A. SQL == PYTHON : each KPI computed by the SQL views/function is recomputed
     independently from the raw tables with pandas and compared cell by cell.
  B. DATASET PROPERTIES : the generated data must exhibit what the KPIs are meant to
     reveal (Monday/Friday effect, winter peak, manager spread, burnout alerts that
     correlate with absences, ...), and respect the brief (3-4 tables, 5,000-50,000 rows).

Exit code 0 = everything passes. A text report is written to verification_report.txt.
"""
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

ROOT = Path(__file__).resolve().parent.parent
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def fetch(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def expected_alerts(wl, ab, as_of, hours, weeks, leave_days):
    """Independent re-implementation of KPI 2 (no SQL logic reused)."""
    last_week = as_of - dt.timedelta(days=as_of.weekday())
    needed = [last_week - dt.timedelta(days=7 * k) for k in range(weeks)]
    sub = wl[wl["week_start"].isin(needed)]
    g = sub.groupby("employee_id")["hours"].agg(["count", "min"])
    hot = set(g[(g["count"] == weeks) & (g["min"] > hours)].index)
    lv = ab[(ab["absence_type"] == "Planned leave")
            & (ab["start_date"] > as_of - dt.timedelta(days=leave_days))
            & (ab["start_date"] <= as_of)]
    return hot - set(lv["employee_id"])


def main():
    with psycopg.connect("") as conn:
        emp = fetch(conn, "SELECT * FROM employees")
        managers = fetch(conn, "SELECT employee_id, manager_id FROM employee_managers")
        dept = fetch(conn, "SELECT * FROM departments")
        wl = fetch(conn, "SELECT employee_id, week_start, hours_worked FROM weekly_workload")
        ab = fetch(conn, "SELECT employee_id, start_date, end_date, absence_type, reason, is_justified FROM absences")
        wl["hours"] = wl["hours_worked"].astype(float)
        wl["week_start"] = pd.to_datetime(wl["week_start"]).dt.date
        ab["start_date"] = pd.to_datetime(ab["start_date"]).dt.date
        ab["end_date"] = pd.to_datetime(ab["end_date"]).dt.date
        n_emp = len(emp)

        # ------------------------------------------------------------ brief
        n_tables = fetch(conn, "SELECT COUNT(*) c FROM information_schema.tables "
                               "WHERE table_schema='public' AND table_type='BASE TABLE'")["c"][0]
        check("Brief: 3 to 5 related tables", 3 <= n_tables <= 5, f"{n_tables} tables")
        check("Brief: main table (absences) has 5,000-50,000 rows", 5000 <= len(ab) <= 50000, f"{len(ab):,} rows")
        n_fk = fetch(conn, "SELECT COUNT(*) c FROM information_schema.table_constraints "
                           "WHERE constraint_type='FOREIGN KEY' AND table_schema='public'")["c"][0]
        check("Brief: tables are related (foreign keys)", n_fk >= 4, f"{n_fk} foreign keys")

        # ---------------------------------------------- KPI 1: SQL == Python
        wl["ot"] = np.maximum(wl["hours"] - 40, 0)
        m = wl.merge(emp[["employee_id", "dept_id"]], on="employee_id").merge(dept, on="dept_id")
        m["month"] = pd.to_datetime(m["week_start"]).dt.to_period("M").dt.to_timestamp()
        py1 = (m.groupby(["dept_name", "month"])
                 .agg(py_avg=("ot", "mean"), py_sum=("ot", "sum"), py_n=("employee_id", "nunique"))
                 .reset_index())
        py1["py_per_emp"] = py1["py_sum"] / py1["py_n"]
        sql1 = fetch(conn, "SELECT * FROM v_kpi1_overtime_by_dept_month")
        sql1["month"] = pd.to_datetime(sql1["month"])
        sql1[["avg_weekly_overtime_h", "overtime_h_per_employee_month"]] = \
            sql1[["avg_weekly_overtime_h", "overtime_h_per_employee_month"]].astype(float)
        j1 = py1.merge(sql1, on=["dept_name", "month"], how="outer", indicator=True)
        check("KPI 1: SQL and Python cover the same dept-month cells", (j1["_merge"] == "both").all(),
              f"{len(j1)} cells")
        both = j1[j1["_merge"] == "both"]
        d_avg = (both["py_avg"] - both["avg_weekly_overtime_h"]).abs().max()
        d_mon = (both["py_per_emp"] - both["overtime_h_per_employee_month"]).abs().max()
        check("KPI 1: AVG(overtime_hours) matches Python", d_avg <= 0.0051, f"max diff {d_avg:.4f}")
        check("KPI 1: SUM/COUNT(DISTINCT emp) per month matches Python", d_mon <= 0.0051, f"max diff {d_mon:.4f}")
        n_months = m["month"].nunique()
        check("KPI 1: every department has a value for every month", len(sql1) == len(dept) * n_months,
              f"{len(sql1)} = {len(dept)} depts x {n_months} months")
        spread = sql1["avg_weekly_overtime_h"].max() / sql1["avg_weekly_overtime_h"].min()
        check("KPI 1: overtime varies enough between dept/months to drive a decision (max/min >= 1.3)",
              spread >= 1.3, f"max/min = {spread:.2f}")
        by_dept = sql1.groupby("dept_name")["avg_weekly_overtime_h"].mean()
        check("KPI 1: departments differ (highest dept >= 1.2 x lowest)",
              by_dept.max() / by_dept.min() >= 1.2, f"{by_dept.round(2).to_dict()}")

        # ---------------------------------------------- KPI 2: SQL == Python
        as_of = max(wl["week_start"]) + dt.timedelta(days=6)
        for label, args, sql_args in [
            ("default (50 h, 4 weeks, 90 days)", (as_of, 50, 4, 90), "NULL, 50, 4, 90"),
            ("as-of 2025-09-30, 48 h, 3 weeks, 60 days", (dt.date(2025, 9, 30), 48, 3, 60),
             "DATE '2025-09-30', 48, 3, 60"),
            ("as-of 2025-06-30, 52 h, 4 weeks, 90 days", (dt.date(2025, 6, 30), 52, 4, 90),
             "DATE '2025-06-30', 52, 4, 90"),
        ]:
            exp = expected_alerts(wl, ab, *args)
            got = set(fetch(conn, f"SELECT employee_id FROM fn_burnout_alerts({sql_args})")["employee_id"])
            check(f"KPI 2: alert list SQL == Python, {label}", exp == got,
                  f"{len(got)} alerts (python {len(exp)})")
        alerts = set(fetch(conn, "SELECT employee_id FROM fn_burnout_alerts()")["employee_id"])
        share = len(alerts) / n_emp
        check("KPI 2: alert population is realistic (2%-10% of employees)", 0.02 <= share <= 0.10,
              f"{len(alerts)} of {n_emp} = {100 * share:.1f}%")
        last4 = wl[wl["week_start"] >= as_of - dt.timedelta(days=27 + as_of.weekday())]
        g4 = last4.groupby("employee_id")["hours"].agg(["count", "min"])
        streak_only = set(g4[(g4["count"] == 4) & (g4["min"] > 50)].index)
        near = streak_only - alerts
        check("KPI 2: both conditions matter (some employees have the streak but took leave)",
              len(near) > 0, f"{len(near)} employees excluded because of leave")
        un = ab[ab["absence_type"] == "Unplanned"].groupby("employee_id").size().reindex(emp["employee_id"], fill_value=0)
        in_alert = un[un.index.isin(alerts)].mean()
        others = un[~un.index.isin(alerts)].mean()
        check("KPI 2: alerted employees are absent more often (ratio >= 1.15)", in_alert / others >= 1.15,
              f"{in_alert:.1f} vs {others:.1f} unplanned days per employee")
        hist = fetch(conn, "SELECT COUNT(DISTINCT employee_id) c FROM v_kpi2_streak_history")["c"][0]
        check("KPI 2: streak-history query finds past episodes too", hist > len(alerts), f"{hist} employees")

        # ---------------------------------------------- KPI 3: SQL == Python
        start = min(wl["week_start"])
        end = max(wl["week_start"]) + dt.timedelta(days=6)
        days = pd.bdate_range(start, end)
        wd_days = pd.Series(days.dayofweek).value_counts()          # 0=Mon .. 4=Fri
        team = managers.dropna(subset=["manager_id"]).groupby("manager_id").size()
        un_df = ab[ab["absence_type"] == "Unplanned"].merge(managers, on="employee_id")
        un_df = un_df.dropna(subset=["manager_id"])
        un_df["wd"] = pd.to_datetime(un_df["start_date"]).dt.dayofweek
        cnt = un_df.groupby(["manager_id", "wd"]).size()
        unj = un_df[~un_df["is_justified"]].groupby(["manager_id", "wd"]).size()
        rows = []
        for mg, ts in team.items():
            for wd in range(5):
                tot = ts * wd_days[wd]
                rows.append((int(mg), wd + 1, tot, cnt.get((mg, wd), 0), unj.get((mg, wd), 0)))
        py3 = pd.DataFrame(rows, columns=["manager_id", "weekday", "py_tot", "py_un", "py_unj"])
        py3["py_rate"] = 100.0 * py3["py_un"] / py3["py_tot"]
        py3["py_unj_rate"] = 100.0 * py3["py_unj"] / py3["py_tot"]
        sql3 = fetch(conn, "SELECT * FROM v_kpi3_unplanned_rate_by_manager_weekday")
        sql3["manager_id"] = sql3["manager_id"].astype(int)
        sql3[["unplanned_rate_pct", "unjustified_rate_pct"]] = sql3[["unplanned_rate_pct", "unjustified_rate_pct"]].astype(float)
        j3 = py3.merge(sql3, on=["manager_id", "weekday"], how="outer", indicator=True)
        check("KPI 3: SQL and Python cover the same manager-weekday cells", (j3["_merge"] == "both").all(),
              f"{len(j3)} cells ({team.size} managers x 5 weekdays)")
        b = j3[j3["_merge"] == "both"]
        check("KPI 3: denominators (total working days) match", (b["py_tot"] == b["total_work_days"]).all())
        check("KPI 3: unplanned-day counts match", (b["py_un"] == b["unplanned_days"]).all())
        d_r = (b["py_rate"] - b["unplanned_rate_pct"]).abs().max()
        d_u = (b["py_unj_rate"] - b["unjustified_rate_pct"]).abs().max()
        check("KPI 3: unplanned rate % matches Python", d_r <= 0.0051, f"max diff {d_r:.4f}")
        check("KPI 3: unjustified rate % matches Python", d_u <= 0.0051, f"max diff {d_u:.4f}")

        wk = fetch(conn, "SELECT weekday, unplanned_rate_pct::float r, unjustified_rate_pct::float u "
                         "FROM v_kpi3_by_weekday ORDER BY weekday")
        mid = wk[wk["weekday"].isin([2, 3, 4])]["r"].mean()
        mon, fri = wk.loc[wk.weekday == 1, "r"].iloc[0], wk.loc[wk.weekday == 5, "r"].iloc[0]
        check("KPI 3: Monday effect (Monday rate >= 1.15 x mid-week)", mon >= 1.15 * mid,
              f"Mon {mon:.2f}% vs Tue-Thu {mid:.2f}%")
        check("KPI 3: Friday effect (Friday rate >= 1.15 x mid-week)", fri >= 1.15 * mid,
              f"Fri {fri:.2f}% vs Tue-Thu {mid:.2f}%")
        u_mid = wk[wk["weekday"].isin([2, 3, 4])]["u"].mean()
        u_edge = wk[wk["weekday"].isin([1, 5])]["u"].mean()
        check("KPI 3: unjustified absences concentrate on Monday/Friday", u_edge > u_mid * 1.2,
              f"{u_edge:.2f}% vs {u_mid:.2f}%")
        mg = fetch(conn, "SELECT unplanned_rate_pct::float r FROM v_kpi3_by_manager")["r"]
        check("KPI 3: enough managers to compare (>= 20)", len(mg) >= 20, f"{len(mg)} managers")
        check("KPI 3: manager spread (worst >= 1.5 x median)", mg.max() >= 1.5 * mg.median(),
              f"worst {mg.max():.2f}% vs median {mg.median():.2f}%")

        # ------------------------------------------- realism of the data
        a_un = ab[ab["absence_type"] == "Unplanned"].copy()
        a_un["month"] = pd.to_datetime(a_un["start_date"]).dt.month
        wd_by_month = pd.Series(days.month).value_counts()
        def rate(months):
            return a_un["month"].isin(months).sum() / (n_emp * sum(wd_by_month.get(x, 0) for x in months))
        winter, summer = rate([12, 1, 2]), rate([6, 7, 8])
        check("Realism: unplanned absences peak in winter (Dec-Feb >= 1.1 x Jun-Aug)", winter >= 1.1 * summer,
              f"{100 * winter:.2f}% vs {100 * summer:.2f}% of employee-days")
        ot_emp = wl.groupby("employee_id")["ot"].mean().reindex(emp["employee_id"])
        corr = np.corrcoef(ot_emp.values, un.values)[0, 1]
        check("Realism: employees with more overtime are absent more (correlation >= 0.10)", corr >= 0.10,
              f"r = {corr:.2f}")
        overall = len(a_un) / (n_emp * len(days))
        check("Realism: overall unplanned absence rate plausible (1.5%-5%)", 0.015 <= overall <= 0.05,
              f"{100 * overall:.2f}%")
        missing = 1 - len(wl) / (n_emp * wl["week_start"].nunique())
        check("Realism: a few weeks are missing (0.2%-1.5%) so data-quality issues are real",
              0.002 <= missing <= 0.015, f"{100 * missing:.2f}% of employee-weeks missing")

        # ------------------------------------------- integrity
        bad_dept = fetch(conn, "SELECT COUNT(*) c FROM employee_managers em "
                               "JOIN employees e ON e.employee_id=em.employee_id "
                               "JOIN employees m ON m.employee_id=em.manager_id "
                               "WHERE m.dept_id <> e.dept_id")["c"][0]
        check("Integrity: every manager belongs to the same department as the team", bad_dept == 0, f"{bad_dept} violations")
        pre_hire = fetch(conn, "SELECT COUNT(*) c FROM absences a JOIN employees e USING (employee_id) "
                               "WHERE a.start_date < e.hire_date")["c"][0]
        check("Integrity: no absence before the hire date", pre_hire == 0, f"{pre_hire} violations")

    width = max(len(n) for n, _, _ in RESULTS)
    lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(width)}  {d}" for n, ok, d in RESULTS]
    n_ok = sum(ok for _, ok, _ in RESULTS)
    lines.append("")
    lines.append(f"{n_ok}/{len(RESULTS)} checks passed")
    text = "\n".join(lines)
    print(text)
    (ROOT / "verification_report.txt").write_text(text + "\n")
    sys.exit(0 if n_ok == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
