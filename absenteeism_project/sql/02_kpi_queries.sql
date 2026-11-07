-- =====================================================================
-- 02_kpi_queries.sql  |  KPI views and functions for the 3 business decisions
-- Run after 01_schema.sql and after the data is loaded. Re-runnable.
-- Owner: Role B (SQL analyst) -- delivered here so the whole pipeline can be verified.
-- =====================================================================

-- Reporting period = the weeks present in weekly_workload ---------------
CREATE OR REPLACE VIEW v_reporting_period AS
SELECT MIN(week_start)     AS period_start,
       MAX(week_start) + 6 AS period_end          -- Monday + 6 = Sunday
FROM weekly_workload;

-- ---------------------------------------------------------------------
-- DECISION 1 - Proactive workload reallocation
-- KPI 1: average overtime per department and month
--   avg_weekly_overtime_h          = AVG(overtime_hours)                        (per employee-week)
--   overtime_h_per_employee_month  = SUM(overtime_hours) / COUNT(DISTINCT emp)  (monthly total per head)
-- A week belongs to the month of its Monday.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi1_overtime_by_dept_month AS
SELECT d.dept_name,
       date_trunc('month', w.week_start)::date                              AS month,
       COUNT(DISTINCT w.employee_id)                                        AS employees,
       ROUND(AVG(w.overtime_hours), 2)                                      AS avg_weekly_overtime_h,
       ROUND(SUM(w.overtime_hours) / COUNT(DISTINCT w.employee_id), 2)      AS overtime_h_per_employee_month
FROM weekly_workload w
JOIN employees   e USING (employee_id)
JOIN departments d USING (dept_id)
GROUP BY d.dept_name, date_trunc('month', w.week_start);

-- ---------------------------------------------------------------------
-- DECISION 2 - Early burnout detection
-- KPI 2: burnout alert = more than p_hours per week for each of the last
--        p_weeks consecutive weeks (ending at the week of p_as_of)
--        AND zero planned-leave days in the last p_leave_days days.
-- Defaults: 50 h, 4 weeks, 90 days, as-of = last day of the period.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_burnout_alerts(
    p_as_of      date    DEFAULT NULL,
    p_hours      numeric DEFAULT 50,
    p_weeks      int     DEFAULT 4,
    p_leave_days int     DEFAULT 90)
RETURNS TABLE (employee_id int, dept_name text, manager_id int,
               avg_hours_recent numeric, min_hours_recent numeric, leave_days_in_window int)
LANGUAGE sql STABLE AS $$
WITH p AS (
    SELECT COALESCE(p_as_of, (SELECT period_end FROM v_reporting_period)) AS as_of
), win AS (
    SELECT as_of, date_trunc('week', as_of)::date AS last_week FROM p
), recent AS (
    SELECT w.employee_id,
           COUNT(*)            AS n_weeks,
           AVG(w.hours_worked) AS avg_h,
           MIN(w.hours_worked) AS min_h
    FROM weekly_workload w, win
    WHERE w.week_start BETWEEN win.last_week - 7 * (p_weeks - 1) AND win.last_week
    GROUP BY w.employee_id
), streak AS (                                  -- every one of the p_weeks weeks present and above the threshold
    SELECT * FROM recent WHERE n_weeks = p_weeks AND min_h > p_hours
), leave AS (
    SELECT a.employee_id, COUNT(*) AS leave_days
    FROM absences a, win
    WHERE a.absence_type = 'Planned leave'
      AND a.absence_date >  win.as_of - p_leave_days
      AND a.absence_date <= win.as_of
    GROUP BY a.employee_id
)
SELECT s.employee_id, d.dept_name, e.manager_id,
       ROUND(s.avg_h, 1), s.min_h, COALESCE(l.leave_days, 0)::int
FROM streak s
JOIN employees   e ON e.employee_id = s.employee_id
JOIN departments d ON d.dept_id     = e.dept_id
LEFT JOIN leave  l ON l.employee_id = s.employee_id
WHERE l.employee_id IS NULL                      -- no leave taken in the window
$$;

CREATE OR REPLACE VIEW v_kpi2_alerts_by_dept AS
SELECT d.dept_name,
       COUNT(a.employee_id)                                         AS alerts,
       COUNT(*)                                                     AS headcount,
       ROUND(100.0 * COUNT(a.employee_id) / COUNT(*), 2)            AS alert_rate_pct
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
LEFT JOIN fn_burnout_alerts() a ON a.employee_id = e.employee_id
GROUP BY d.dept_name;

-- Diagnostic: every run of >= 4 consecutive weeks above 50 h (gaps-and-islands) ----
CREATE OR REPLACE VIEW v_kpi2_streak_history AS
WITH hot AS (
    SELECT employee_id, week_start
    FROM weekly_workload WHERE hours_worked > 50
), grp AS (
    SELECT employee_id, week_start,
           week_start - (ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY week_start))::int * 7 AS island
    FROM hot
)
SELECT employee_id,
       MIN(week_start) AS streak_start,
       MAX(week_start) AS streak_end,
       COUNT(*)        AS weeks
FROM grp
GROUP BY employee_id, island
HAVING COUNT(*) >= 4;

-- ---------------------------------------------------------------------
-- DECISION 3 - Wellbeing action plan and management optimisation
-- KPI 3: unplanned-absence rate = unplanned absence days / total working days,
--        by weekday and by manager.
--   total working days of a manager's team = team size x number of that weekday in the period
--   (Mon-Fri week; public holidays are not modelled)
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_kpi3_unplanned_rate_by_manager_weekday AS
WITH per AS (
    SELECT * FROM v_reporting_period
), cal AS (
    SELECT EXTRACT(ISODOW FROM g)::int AS weekday, COUNT(*) AS work_days
    FROM per, generate_series(per.period_start::timestamp, per.period_end::timestamp, interval '1 day') g
    WHERE EXTRACT(ISODOW FROM g) BETWEEN 1 AND 5
    GROUP BY 1
), team AS (
    SELECT manager_id, COUNT(*) AS team_size
    FROM employees WHERE manager_id IS NOT NULL GROUP BY manager_id
), den AS (
    SELECT t.manager_id, c.weekday, t.team_size, t.team_size * c.work_days AS total_work_days
    FROM team t CROSS JOIN cal c
), num AS (
    SELECT e.manager_id, a.weekday,
           COUNT(*) FILTER (WHERE a.absence_type = 'Unplanned')                          AS unplanned_days,
           COUNT(*) FILTER (WHERE a.absence_type = 'Unplanned' AND NOT a.is_justified)   AS unjustified_days
    FROM absences a
    JOIN employees e USING (employee_id)
    WHERE e.manager_id IS NOT NULL
    GROUP BY e.manager_id, a.weekday
)
SELECT den.manager_id,
       den.weekday,
       (ARRAY['Mon','Tue','Wed','Thu','Fri'])[den.weekday]                     AS weekday_name,
       den.team_size,
       den.total_work_days,
       COALESCE(num.unplanned_days, 0)                                         AS unplanned_days,
       COALESCE(num.unjustified_days, 0)                                       AS unjustified_days,
       ROUND(100.0 * COALESCE(num.unplanned_days, 0)   / den.total_work_days, 2) AS unplanned_rate_pct,
       ROUND(100.0 * COALESCE(num.unjustified_days, 0) / den.total_work_days, 2) AS unjustified_rate_pct
FROM den
LEFT JOIN num USING (manager_id, weekday);

-- all managers together, by weekday (Monday / Friday effect)
CREATE OR REPLACE VIEW v_kpi3_by_weekday AS
SELECT weekday, weekday_name,
       SUM(total_work_days)  AS total_work_days,
       SUM(unplanned_days)   AS unplanned_days,
       SUM(unjustified_days) AS unjustified_days,
       ROUND(100.0 * SUM(unplanned_days)   / SUM(total_work_days), 2) AS unplanned_rate_pct,
       ROUND(100.0 * SUM(unjustified_days) / SUM(total_work_days), 2) AS unjustified_rate_pct
FROM v_kpi3_unplanned_rate_by_manager_weekday
GROUP BY weekday, weekday_name;

-- by manager over the whole week, ranked (worst first)
CREATE OR REPLACE VIEW v_kpi3_by_manager AS
SELECT manager_id,
       MAX(team_size)                                                   AS team_size,
       SUM(unplanned_days)                                              AS unplanned_days,
       ROUND(100.0 * SUM(unplanned_days) / SUM(total_work_days), 2)     AS unplanned_rate_pct,
       RANK() OVER (ORDER BY SUM(unplanned_days)::numeric / SUM(total_work_days) DESC) AS rank_worst_first
FROM v_kpi3_unplanned_rate_by_manager_weekday
GROUP BY manager_id;

-- reason (motif) x weekday: share of each reason among unplanned absences of that weekday
CREATE OR REPLACE VIEW v_kpi3_reason_by_weekday AS
SELECT weekday, reason, COUNT(*) AS absence_days,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY weekday), 1) AS share_of_weekday_pct
FROM absences
WHERE absence_type = 'Unplanned'
GROUP BY weekday, reason;
