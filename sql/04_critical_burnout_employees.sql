-- Employees in CRITICAL burnout zone
-- Criteria: (avg weekly hours > 48 OR max weekly hours > 58) AND annual leave days < 10
-- Supports decision: Which individuals need immediate intervention?

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
