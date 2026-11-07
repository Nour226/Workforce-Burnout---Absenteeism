-- =====================================================================
-- 01_schema.sql  |  Workforce Burnout & Employee Absenteeism
-- PostgreSQL 14+ | Owner: Role A (data engineer)
-- Re-runnable: drops and recreates everything.
-- =====================================================================

DROP VIEW     IF EXISTS v_kpi3_reason_by_weekday, v_kpi3_by_manager, v_kpi3_by_weekday,
                        v_kpi3_unplanned_rate_by_manager_weekday,
                        v_kpi2_alerts_by_dept, v_kpi2_streak_history,
                        v_kpi1_overtime_by_dept_month, v_reporting_period CASCADE;
DROP FUNCTION IF EXISTS fn_burnout_alerts(date, numeric, int, int);
DROP TABLE    IF EXISTS absences, weekly_workload, employees, departments CASCADE;

-- 1. departments ------------------------------------------------------
CREATE TABLE departments (
    dept_id    smallint PRIMARY KEY,
    dept_name  text     NOT NULL UNIQUE
);

-- 2. employees --------------------------------------------------------
-- Base: IBM HR Analytics Employee Attrition & Performance (see README).
-- manager_id is a self-reference (NULL = top of the hierarchy).
CREATE TABLE employees (
    employee_id        integer  PRIMARY KEY,
    dept_id            smallint NOT NULL REFERENCES departments (dept_id),
    manager_id         integer  REFERENCES employees (employee_id),
    job_role           text     NOT NULL,
    gender             text     NOT NULL CHECK (gender IN ('Male', 'Female')),
    age                smallint NOT NULL CHECK (age BETWEEN 18 AND 70),
    overtime_flag      boolean  NOT NULL,          -- IBM "OverTime" (Yes/No)
    job_satisfaction   smallint NOT NULL CHECK (job_satisfaction BETWEEN 1 AND 4),
    work_life_balance  smallint NOT NULL CHECK (work_life_balance BETWEEN 1 AND 4),
    distance_from_home smallint NOT NULL CHECK (distance_from_home >= 0),
    years_at_company   smallint NOT NULL CHECK (years_at_company >= 0),
    hire_date          date     NOT NULL,
    CHECK (manager_id IS DISTINCT FROM employee_id)
);

-- 3. weekly_workload --------------------------------------------------
-- One row per employee per week (week_start = Monday). Source of KPI 1 and KPI 2.
CREATE TABLE weekly_workload (
    workload_id    integer      PRIMARY KEY,
    employee_id    integer      NOT NULL REFERENCES employees (employee_id),
    week_start     date         NOT NULL CHECK (EXTRACT(ISODOW FROM week_start) = 1),
    hours_worked   numeric(4,1) NOT NULL CHECK (hours_worked BETWEEN 0 AND 90),
    -- hours above the 40 h contractual week
    overtime_hours numeric(4,1) GENERATED ALWAYS AS (GREATEST(hours_worked - 40, 0)) STORED,
    UNIQUE (employee_id, week_start)
);

-- 4. absences (main table) ---------------------------------------------
-- One row per employee per absent working day (Mon-Fri). Source of KPI 2 (leave) and KPI 3.
CREATE TABLE absences (
    absence_id   integer  PRIMARY KEY,
    employee_id  integer  NOT NULL REFERENCES employees (employee_id),
    absence_date date     NOT NULL CHECK (EXTRACT(ISODOW FROM absence_date) BETWEEN 1 AND 5),
    weekday      smallint GENERATED ALWAYS AS (EXTRACT(ISODOW FROM absence_date)::smallint) STORED,
    absence_type text     NOT NULL CHECK (absence_type IN ('Planned leave', 'Unplanned')),
    reason       text     NOT NULL,
    is_justified boolean  NOT NULL,
    UNIQUE (employee_id, absence_date)
);

-- Indexes (foreign keys and the filters the KPI queries use) ------------
CREATE INDEX ix_employees_dept       ON employees (dept_id);
CREATE INDEX ix_employees_manager    ON employees (manager_id);
CREATE INDEX ix_workload_week        ON weekly_workload (week_start);
CREATE INDEX ix_absences_date        ON absences (absence_date);
CREATE INDEX ix_absences_type_date   ON absences (absence_type, absence_date);
