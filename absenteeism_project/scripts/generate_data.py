#!/usr/bin/env python3
"""
generate_data.py  |  Role A (data engineer)

Builds the 4 CSV files loaded into PostgreSQL:
    departments.csv, employees.csv, weekly_workload.csv, absences.csv

HYBRID DATASET
  * employees / departments  <- IBM HR Analytics Employee Attrition & Performance (Kaggle)
        pass the real file with  --ibm path/to/WA_Fn-UseC_-HR-Employee-Attrition.csv
        without --ibm, a STAND-IN with the same columns and approximate IBM
        distributions is generated (used when the file cannot be downloaded).
  * weekly_workload, absences, manager hierarchy, burnout score <- SYNTHETIC (rules below)

Everything is seeded: same seed -> same files.

Rules the synthetic part follows (so the 3 KPIs are meaningful):
  KPI 1  weekly hours depend on IBM OverTime / WorkLifeBalance / JobSatisfaction,
         department and season (March, June, Nov-Dec peaks).
  KPI 2  ~6% of employees are in a "crunch" ending at the last week (>50 h for
         5-8 weeks); most of them take no leave in the last ~100 days. Other
         employees have older crunch episodes. Burnout-prone employees take
         less leave.
  KPI 3  unplanned absences are more frequent on Monday and Friday, in winter,
         for burnout-prone employees, after heavy weeks, and in some managers'
         teams; Mon/Fri absences are less often justified.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PERIOD_START = pd.Timestamp("2025-01-06")  # a Monday
N_WEEKS = 52
N_DAYS = N_WEEKS * 5                         # working days Mon-Fri
DEPARTMENTS = ["Human Resources", "Research & Development", "Sales"]

ROLES = {
    "Research & Development": (
        ["Research Scientist", "Laboratory Technician", "Manufacturing Director",
         "Healthcare Representative", "Research Director", "Manager"],
        [0.30, 0.27, 0.15, 0.14, 0.08, 0.06]),
    "Sales": (["Sales Executive", "Sales Representative", "Manager"], [0.73, 0.19, 0.08]),
    "Human Resources": (["Human Resources", "Manager"], [0.83, 0.17]),
}

REASONS = ["Illness (flu, cold)", "Medical consultation", "Back pain / musculoskeletal",
           "Dental consultation", "Family emergency", "Transport issue",
           "Stress / fatigue", "Unjustified absence"]
REASON_W = np.array([0.30, 0.17, 0.08, 0.06, 0.08, 0.05, 0.10, 0.16])


def standin_ibm(rng, n=1470):
    """Same columns as the IBM file, approximate IBM marginals."""
    dept = rng.choice(["Research & Development", "Sales", "Human Resources"], size=n,
                      p=[0.6537, 0.3034, 0.0429])
    role = np.empty(n, dtype=object)
    for d, (names, probs) in ROLES.items():
        idx = np.where(dept == d)[0]
        role[idx] = rng.choice(names, size=len(idx), p=probs)
    age = np.clip(rng.normal(36.9, 9.1, n).round(), 18, 60).astype(int)
    years = np.minimum(np.clip(rng.gamma(1.6, 4.4, n).astype(int), 0, 40), age - 18)  # tenure <= working life
    return pd.DataFrame({
        "Age": age,
        "Department": dept,
        "DistanceFromHome": np.clip((rng.exponential(7.5, n) + 1).astype(int), 1, 29),
        "Gender": rng.choice(["Male", "Female"], size=n, p=[0.60, 0.40]),
        "JobRole": role,
        "JobSatisfaction": rng.choice([1, 2, 3, 4], size=n, p=[0.196, 0.190, 0.307, 0.307]),
        "OverTime": rng.choice(["Yes", "No"], size=n, p=[0.283, 0.717]),
        "WorkLifeBalance": rng.choice([1, 2, 3, 4], size=n, p=[0.054, 0.234, 0.607, 0.105]),
        "YearsAtCompany": years,
    })


def load_ibm(path):
    df = pd.read_csv(path)
    need = ["Age", "Department", "DistanceFromHome", "Gender", "JobRole",
            "JobSatisfaction", "OverTime", "WorkLifeBalance", "YearsAtCompany"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(f"IBM file is missing columns: {missing}")
    return df[need].copy()


def build_employees(ibm, rng):
    n = len(ibm)
    dept_id = {name: i + 1 for i, name in enumerate(sorted(ibm["Department"].unique()))}
    emp = pd.DataFrame({
        "employee_id": np.arange(1, n + 1),
        "dept_name": ibm["Department"].values,
        "job_role": ibm["JobRole"].values,
        "gender": ibm["Gender"].values,
        "age": ibm["Age"].values.astype(int),
        "overtime_flag": (ibm["OverTime"].values == "Yes"),
        "job_satisfaction": ibm["JobSatisfaction"].values.astype(int),
        "work_life_balance": ibm["WorkLifeBalance"].values.astype(int),
        "distance_from_home": ibm["DistanceFromHome"].values.astype(int),
        "years_at_company": ibm["YearsAtCompany"].values.astype(int),
    })
    emp["dept_id"] = emp["dept_name"].map(dept_id)
    days_back = emp["years_at_company"].values * 365 + rng.integers(0, 365, n)
    emp["hire_date"] = (pd.Timestamp("2024-12-31") - pd.to_timedelta(days_back, unit="D")).date

    # manager hierarchy: about 1 manager per 12 employees, inside each department
    manager = np.full(n, np.nan)
    for name in dept_id:
        idx = np.where(emp["dept_name"].values == name)[0]
        k = max(1, int(round(len(idx) / 12)))
        roles = emp["job_role"].values[idx]
        senior = idx[[("Manager" in r or "Director" in r) for r in roles]]
        junior = np.setdiff1d(idx, senior)
        rng.shuffle(senior)
        rng.shuffle(junior)
        chosen = np.concatenate([senior, junior])[:k]
        mgr_ids = emp["employee_id"].values[chosen]
        for i in np.setdiff1d(idx, chosen):
            manager[i] = rng.choice(mgr_ids)
    emp["manager_id"] = manager
    return emp, dept_id


def burnout_propensity(emp, rng):
    """Standardised latent score, higher = more burnout-prone (hidden, not stored)."""
    raw = (1.2 * emp["overtime_flag"].values
           + 0.35 * (4 - emp["job_satisfaction"].values)
           + 0.40 * (3 - emp["work_life_balance"].values)
           + 0.02 * emp["distance_from_home"].values
           + rng.normal(0, 0.6, len(emp)))
    return (raw - raw.mean()) / raw.std()


def build_hours(emp, z, rng):
    n = len(emp)
    ot = emp["overtime_flag"].values.astype(float)
    dept_eff = emp["dept_name"].map({"Sales": 0.8, "Human Resources": -0.8}).fillna(0.0).values
    weeks = PERIOD_START + pd.to_timedelta(np.arange(N_WEEKS) * 7, unit="D")
    month = np.asarray(weeks.month)
    season = np.select([month == 3, month == 6, month >= 11], [1.5, 1.0, 2.0], 0.0)

    mean = 40 + 1.2 * z + 3.5 * ot + dept_eff
    H = np.zeros((n, N_WEEKS))
    state = rng.normal(0, 3.9, n)
    for t in range(N_WEEKS):                     # AR(1): heavy weeks tend to follow heavy weeks
        state = 0.65 * state + rng.normal(0, 3.0, n)
        H[:, t] = mean + season[t] + state

    # crunch ending at the last week (will feed KPI 2) -------------------
    p = np.clip(0.06 * np.exp(0.8 * z) / np.exp(0.8 * z).mean(), 0, 0.5)
    crunch_end = rng.random(n) < p
    for i in np.where(crunch_end)[0]:
        length = int(rng.integers(5, 9))
        H[i, -length:] = rng.uniform(51.5, 62.0, length)
    # older crunch episodes elsewhere in the year (history for the streak query)
    old = (rng.random(n) < 0.05) & ~crunch_end
    for i in np.where(old)[0]:
        length = int(rng.integers(4, 8))
        start = int(rng.integers(4, N_WEEKS - 14))
        H[i, start:start + length] = rng.uniform(50.8, 60.0, length)

    H = np.clip(H, 28, 75).round(1)
    return H, weeks, crunch_end


def build_leave(emp, z, crunch_end, bdays, rng):
    """Boolean matrix (employee x working day) of planned leave."""
    n = len(emp)
    month_w = np.array([0.8, 0.7, 0.8, 0.9, 0.9, 1.0, 2.2, 2.8, 1.0, 0.8, 0.8, 1.5])[bdays.month - 1]
    leave = np.zeros((n, N_DAYS), bool)
    no_leave_last = crunch_end & (rng.random(n) < 0.60)       # crunch AND no recent leave
    for i in range(n):
        target = int(np.clip(round(rng.normal(20 - 3.0 * z[i], 5)), 0, 32))
        w = month_w.copy()
        if no_leave_last[i]:
            w[-70:] = 0.0                                      # ~ last 100 calendar days
        w = w / w.sum()
        taken = 0
        guard = 0
        while taken < target and guard < 40:
            guard += 1
            length = int(rng.choice([1, 2, 3, 5, 5, 10]))
            length = min(length, target - taken)
            s = int(rng.choice(N_DAYS, p=w))
            e = min(s + length, N_DAYS)
            if no_leave_last[i]:
                e = min(e, N_DAYS - 70)
            seg = leave[i, s:e]
            taken += int((~seg).sum())
            leave[i, s:e] = True
    return leave


def build_unplanned(emp, z, H, leave, bdays, rng):
    n = len(emp)
    wd = np.array([1.55, 0.90, 0.80, 0.85, 1.35])[np.arange(N_DAYS) % 5]
    mo = np.array([1.35, 1.25, 1.05, 1.00, 0.95, 0.90, 0.90, 0.90, 1.00, 1.00, 1.00, 1.30])[bdays.month - 1]
    hours_day = H[:, np.arange(N_DAYS) // 5]
    P = (0.017 * wd[None, :] * mo[None, :] * np.exp(0.30 * z)[:, None]
         * (1 + 0.02 * np.maximum(hours_day - 45, 0)))

    # manager effect: lognormal, plus two clearly worse teams
    mgr_ids = emp["manager_id"].dropna().astype(int).unique()
    factors = np.exp(rng.normal(0, 0.25, len(mgr_ids)))
    factors[rng.choice(len(factors), 2, replace=False)] *= 1.9
    mf = {int(m): f for m, f in zip(mgr_ids, factors)}
    team_factor = np.array([1.0 if np.isnan(m) else mf[int(m)] for m in emp["manager_id"].values])
    P = P * team_factor[:, None]

    U1, U2 = rng.random((n, N_DAYS)), rng.random((n, N_DAYS))
    absent = np.zeros((n, N_DAYS), bool)
    prev = np.zeros(n, bool)
    for t in range(N_DAYS):
        cont = prev & (U2[:, t] < 0.30) if t % 5 != 0 else np.zeros(n, bool)
        cur = ((U1[:, t] < P[:, t]) | cont) & ~leave[:, t]
        absent[:, t] = cur
        prev = cur
    return absent


def build_absence_rows(emp, z, leave, absent, bdays, rng):
    rows = []
    # planned leave
    ei, ti = np.where(leave)
    rows.append(pd.DataFrame({"employee_id": emp["employee_id"].values[ei], "t": ti,
                              "absence_type": "Planned leave", "reason": "Annual leave",
                              "is_justified": True}))
    # unplanned
    ei, ti = np.where(absent)
    m = len(ei)
    w = np.tile(REASON_W, (m, 1))
    is_edge = (ti % 5 == 0) | (ti % 5 == 4)
    w[:, 7] *= np.where(is_edge, 1.6, 1.0)                 # unjustified more on Mon/Fri
    w[:, 6] *= np.exp(0.6 * z[ei])                         # stress more for burnout-prone
    w = w / w.sum(axis=1, keepdims=True)
    pick = (rng.random(m)[:, None] > np.cumsum(w, axis=1)).sum(axis=1).clip(0, len(REASONS) - 1)
    reason = np.array(REASONS)[pick]
    justified = np.where(reason == "Unjustified absence", False,
                         np.where(reason == "Transport issue", rng.random(m) < 0.5,
                                  rng.random(m) < 0.95))
    rows.append(pd.DataFrame({"employee_id": emp["employee_id"].values[ei], "t": ti,
                              "absence_type": "Unplanned", "reason": reason,
                              "is_justified": justified}))
    ab = pd.concat(rows, ignore_index=True)
    ab["absence_date"] = bdays[ab["t"].values].date
    ab = ab.sort_values(["absence_date", "employee_id"]).reset_index(drop=True)
    ab.insert(0, "absence_id", np.arange(1, len(ab) + 1))
    return ab[["absence_id", "employee_id", "absence_date", "absence_type", "reason", "is_justified"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ibm", help="path to the real IBM HR CSV (optional)")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.ibm:
        ibm, mode = load_ibm(args.ibm), "REAL IBM HR file"
    else:
        ibm, mode = standin_ibm(rng), "STAND-IN with IBM structure (real file not supplied)"
    emp, dept_id = build_employees(ibm, rng)
    z = burnout_propensity(emp, rng)
    H, weeks, crunch_end = build_hours(emp, z, rng)
    bdays = pd.bdate_range(PERIOD_START, periods=N_DAYS)
    leave = build_leave(emp, z, crunch_end, bdays, rng)
    absent = build_unplanned(emp, z, H, leave, bdays, rng)
    ab = build_absence_rows(emp, z, leave, absent, bdays, rng)

    # weekly_workload; ~0.5% of weeks missing (realistic gaps), never in the last 8 weeks
    ei, wi = np.meshgrid(np.arange(len(emp)), np.arange(N_WEEKS), indexing="ij")
    wl = pd.DataFrame({"employee_id": emp["employee_id"].values[ei.ravel()],
                       "week_start": weeks[wi.ravel()].date,
                       "hours_worked": H.ravel(), "_w": wi.ravel()})
    drop = (rng.random(len(wl)) < 0.005) & (wl["_w"] < N_WEEKS - 8)
    wl = wl[~drop].drop(columns="_w").reset_index(drop=True)
    wl.insert(0, "workload_id", np.arange(1, len(wl) + 1))

    dept = pd.DataFrame({"dept_id": list(dept_id.values()), "dept_name": list(dept_id.keys())})
    emp_out = emp[["employee_id", "dept_id", "manager_id", "job_role", "gender", "age",
                   "overtime_flag", "job_satisfaction", "work_life_balance",
                   "distance_from_home", "years_at_company", "hire_date"]].copy()
    emp_out["manager_id"] = emp_out["manager_id"].astype("Int64")

    dept.to_csv(out / "departments.csv", index=False)
    emp_out.to_csv(out / "employees.csv", index=False)
    wl.to_csv(out / "weekly_workload.csv", index=False)
    ab.to_csv(out / "absences.csv", index=False)

    note = {"employees_source": mode, "seed": args.seed,
            "period": f"{PERIOD_START.date()} to {(PERIOD_START + pd.Timedelta(days=N_WEEKS * 7 - 1)).date()}",
            "rows": {"departments": len(dept), "employees": len(emp_out),
                     "weekly_workload": len(wl), "absences": len(ab)}}
    (out / "generation_note.json").write_text(json.dumps(note, indent=2))
    print(json.dumps(note, indent=2))
    print("unplanned days:", int((ab.absence_type == "Unplanned").sum()),
          "| planned leave days:", int((ab.absence_type == "Planned leave").sum()))


if __name__ == "__main__":
    main()
