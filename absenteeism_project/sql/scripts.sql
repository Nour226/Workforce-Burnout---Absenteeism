-- ============================================================
-- ABSENTEEISM / OVERTIME / BURNOUT ANALYSIS SCRIPTS
--   SURCHARGE CRITIQUE : avg weekly OT > 8.5 h
--   CHARGE ELEVEE      : avg weekly OT > 5.0 h
--   CHARGE NORMALE     : otherwise
-- ============================================================

--R1: ANNUAL OVERTIME BY DEPARTMENT
SELECT
    DENSE_RANK() OVER (
        ORDER BY
            SUM(GREATEST(0, w.hours_worked - 40))
            / NULLIF(COUNT(DISTINCT e.employee_id) * 52, 0) DESC
    ) AS rank_overtime,

    d.dept_name AS department_name,

    COUNT(DISTINCT e.employee_id) AS total_employees,

    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40)),
        2
    ) AS total_annual_overtime_hours,

    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40))
        / NULLIF(COUNT(DISTINCT e.employee_id) * 52, 0),
        2
    ) AS avg_weekly_overtime_per_emp,

    -- Volume annuel en trop (seuil normal de 2h/sem/emp)
    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40)) - (COUNT(DISTINCT e.employee_id) * 52 * 2.00),
        2
    ) AS annual_overtime_excess_hours,

    CASE
        WHEN SUM(GREATEST(0, w.hours_worked - 40))
             / NULLIF(COUNT(DISTINCT e.employee_id) * 52, 0) > 8.5
            THEN 'SURCHARGE CRITIQUE'
        WHEN SUM(GREATEST(0, w.hours_worked - 40))
             / NULLIF(COUNT(DISTINCT e.employee_id) * 52, 0) > 5
            THEN 'CHARGE ELEVEE'
        ELSE 'CHARGE NORMALE'
    END AS department_status

FROM departments d
JOIN employees e
    ON d.dept_id = e.dept_id
JOIN weekly_workload w
    ON e.employee_id = w.employee_id

GROUP BY d.dept_id, d.dept_name
ORDER BY rank_overtime ASC;


--R2: QUARTERLY OVERTIME BY DEPARTMENT (thresholds aligned with annual)
SELECT
    'Q' || EXTRACT(QUARTER FROM w.week_start) AS quarter,

    DENSE_RANK() OVER (
        PARTITION BY EXTRACT(QUARTER FROM w.week_start)
        ORDER BY
            SUM(GREATEST(0, w.hours_worked - 40))
            / NULLIF(COUNT(DISTINCT e.employee_id) * 13, 0) DESC
    ) AS rank_overtime,

    d.dept_name AS department_name,

    COUNT(DISTINCT e.employee_id) AS total_employees,

    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40)),
        2
    ) AS total_quarterly_overtime_hours,

    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40))
        / NULLIF(COUNT(DISTINCT e.employee_id) * 13, 0),
        2
    ) AS avg_weekly_overtime_per_emp,

    -- Volume trimestriel en trop (seuil normal : 2h/sem/emp sur 13 sem)
    ROUND(
        SUM(GREATEST(0, w.hours_worked - 40)) - (COUNT(DISTINCT e.employee_id) * 13 * 2.00),
        2
    ) AS quarterly_overtime_excess_hours,

    CASE
        WHEN SUM(GREATEST(0, w.hours_worked - 40))
             / NULLIF(COUNT(DISTINCT e.employee_id) * 13, 0) > 8.5
            THEN 'SURCHARGE CRITIQUE'
        WHEN SUM(GREATEST(0, w.hours_worked - 40))
             / NULLIF(COUNT(DISTINCT e.employee_id) * 13, 0) > 5
            THEN 'CHARGE ELEVEE'
        ELSE 'CHARGE NORMALE'
    END AS department_status

FROM departments d
JOIN employees e
    ON d.dept_id = e.dept_id
JOIN weekly_workload w
    ON e.employee_id = w.employee_id

GROUP BY EXTRACT(QUARTER FROM w.week_start), d.dept_id, d.dept_name
ORDER BY quarter ASC, rank_overtime ASC;


--R3: EMPLOYEES IN RED ZONE (critical burnout count)
WITH annual_work_metrics AS (
    SELECT 
        employee_id,
        ROUND(AVG(hours_worked), 2) AS avg_weekly_hours,
        MAX(hours_worked) AS max_weekly_hours
    FROM weekly_workload
    GROUP BY employee_id
),
annual_leave_metrics AS (
    SELECT 
        employee_id,
        COALESCE(SUM(end_date - start_date + 1), 0) AS total_vacation_days
    FROM absences
    WHERE absence_type = 'Planned leave' 
      AND reason = 'Annual Leave'
    GROUP BY employee_id
)
SELECT 
    COUNT(e.employee_id) AS critical_burnout_count
FROM employees e
LEFT JOIN annual_work_metrics wm ON e.employee_id = wm.employee_id
LEFT JOIN annual_leave_metrics lm ON e.employee_id = lm.employee_id
WHERE (wm.avg_weekly_hours > 48 OR wm.max_weekly_hours > 58)
  AND COALESCE(lm.total_vacation_days, 0) < 10;


--R4: EMPLOYEES AT RISK LIST (detailed)
WITH annual_work_metrics AS (
    SELECT 
        employee_id,
        ROUND(AVG(hours_worked), 2) AS avg_weekly_hours,
        MAX(hours_worked) AS max_weekly_hours
    FROM weekly_workload
    GROUP BY employee_id
),
annual_leave_metrics AS (
    SELECT 
        employee_id,
        COALESCE(SUM(end_date - start_date + 1), 0) AS total_vacation_days
    FROM absences
    WHERE absence_type = 'Planned leave' 
      AND reason = 'Annual Leave'
    GROUP BY employee_id
)
SELECT 
    e.employee_id,
    e.full_name,
    e.job_role,
    d.dept_name AS department_name,
    wm.avg_weekly_hours,
    wm.max_weekly_hours,
    COALESCE(lm.total_vacation_days, 0) AS total_vacation_days,
    'CRITICAL (High Risk)' AS risk_status
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
LEFT JOIN annual_work_metrics wm ON e.employee_id = wm.employee_id
LEFT JOIN annual_leave_metrics lm ON e.employee_id = lm.employee_id
WHERE (wm.avg_weekly_hours > 48 OR wm.max_weekly_hours > 58)
  AND COALESCE(lm.total_vacation_days, 0) < 10
ORDER BY wm.avg_weekly_hours DESC;


--R5: BURNOUT RISK BETWEEN DEPARTMENTS
WITH annual_work_metrics AS (
    SELECT 
        employee_id,
        ROUND(AVG(hours_worked), 2) AS avg_weekly_hours,
        MAX(hours_worked) AS max_weekly_hours
    FROM weekly_workload
    GROUP BY employee_id
),
annual_leave_metrics AS (
    SELECT 
        employee_id,
        COALESCE(SUM(end_date - start_date + 1), 0) AS total_vacation_days
    FROM absences
    WHERE absence_type = 'Planned leave' 
      AND reason = 'Annual Leave'
    GROUP BY employee_id
),
employee_risk_levels AS (
    SELECT 
        e.employee_id,
        e.dept_id,
        CASE 
            WHEN (wm.avg_weekly_hours > 48 OR wm.max_weekly_hours > 58) 
                 AND COALESCE(lm.total_vacation_days, 0) < 10 THEN 'CRITICAL'
            WHEN (wm.avg_weekly_hours BETWEEN 45 AND 48) 
                 OR COALESCE(lm.total_vacation_days, 0) BETWEEN 10 AND 15 THEN 'WARNING'
            ELSE 'NORMAL'
        END AS risk_level
    FROM employees e
    LEFT JOIN annual_work_metrics wm ON e.employee_id = wm.employee_id
    LEFT JOIN annual_leave_metrics lm ON e.employee_id = lm.employee_id
)
SELECT 
    d.dept_name AS department_name,
    COUNT(er.employee_id) AS total_employees,
    COUNT(CASE WHEN er.risk_level = 'CRITICAL' THEN 1 END) AS critical_count,
    COUNT(CASE WHEN er.risk_level = 'WARNING' THEN 1 END) AS warning_count,
    COUNT(CASE WHEN er.risk_level = 'NORMAL' THEN 1 END) AS normal_count,
    ROUND(
        (COUNT(CASE WHEN er.risk_level = 'CRITICAL' THEN 1 END)::DECIMAL / COUNT(er.employee_id)) * 100, 
        2
    ) AS critical_burnout_rate_pct
FROM departments d
JOIN employee_risk_levels er ON d.dept_id = er.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY critical_burnout_rate_pct DESC;


--R6: ABSENCE SUMMARY BY DEPARTMENT
WITH employee_absence_summary AS (
    SELECT 
        employee_id,
        COALESCE(SUM(end_date - start_date + 1), 0) AS total_absence_days,
        COALESCE(SUM(CASE WHEN absence_type = 'Unplanned' THEN (end_date - start_date + 1) ELSE 0 END), 0) AS unplanned_absence_days,
        COALESCE(SUM(CASE WHEN is_justified = FALSE THEN (end_date - start_date + 1) ELSE 0 END), 0) AS unjustified_absence_days
    FROM absences
    GROUP BY employee_id
)
SELECT 
    d.dept_name AS department_name,
    COUNT(DISTINCT e.employee_id) AS total_employees,
    COALESCE(SUM(eas.total_absence_days), 0) AS total_absence_days,
    COALESCE(SUM(eas.unplanned_absence_days), 0) AS unplanned_absence_days,
    COALESCE(SUM(eas.unjustified_absence_days), 0) AS unjustified_absence_days,
    ROUND(
        (COALESCE(SUM(eas.unplanned_absence_days), 0)::DECIMAL 
        / NULLIF(SUM(eas.total_absence_days), 0)) * 100, 
        2
    ) AS unplanned_absence_rate_pct
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
LEFT JOIN employee_absence_summary eas ON e.employee_id = eas.employee_id
GROUP BY d.dept_id, d.dept_name
ORDER BY unplanned_absence_rate_pct DESC;


--R7: UNPLANNED ABSENCES BY WEEKDAY (derived from start_date)
SELECT 
    EXTRACT(ISODOW FROM a.start_date)::INT AS weekday,   -- 1=Monday ... 7=Sunday
    CASE EXTRACT(ISODOW FROM a.start_date)::INT
        WHEN 1 THEN 'Lundi'
        WHEN 2 THEN 'Mardi'
        WHEN 3 THEN 'Mercredi'
        WHEN 4 THEN 'Jeudi'
        WHEN 5 THEN 'Vendredi'
        WHEN 6 THEN 'Samedi'
        WHEN 7 THEN 'Dimanche'
        ELSE 'Jour inconnu'
    END AS day_name,
    
    COUNT(a.absence_id) AS total_unplanned_events,
    COALESCE(SUM(a.end_date - a.start_date + 1), 0) AS total_lost_days,
    
    ROUND(
        (COUNT(a.absence_id)::DECIMAL / NULLIF(SUM(COUNT(a.absence_id)) OVER(), 0)) * 100, 
        2
    ) AS pct_of_total_unplanned_events

FROM absences a
WHERE a.absence_type = 'Unplanned'
GROUP BY EXTRACT(ISODOW FROM a.start_date)
ORDER BY weekday;


--R8: UNPLANNED ABSENCES BY DEPARTMENT AND REASON
SELECT 
    d.dept_name AS department_name,
    a.reason,
    COUNT(a.absence_id) AS total_absence_events,
    COALESCE(SUM(a.end_date - a.start_date + 1), 0) AS total_lost_days,
    ROUND(
        AVG(a.end_date - a.start_date + 1), 
        2
    ) AS avg_duration_per_event_days
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
JOIN absences a ON e.employee_id = a.employee_id
WHERE a.absence_type = 'Unplanned'
GROUP BY d.dept_id, d.dept_name, a.reason
ORDER BY d.dept_name ASC, total_lost_days DESC;
