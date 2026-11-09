-- Burnout risk distribution by department
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
        (COUNT(CASE WHEN er.risk_level = 'CRITICAL' THEN 1 END)::DECIMAL
         / COUNT(er.employee_id)) * 100,
        2
    ) AS critical_burnout_rate_pct
FROM departments d
JOIN employee_risk_levels er ON d.dept_id = er.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY critical_burnout_rate_pct DESC;
