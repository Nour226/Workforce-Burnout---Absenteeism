-- KPI: Unplanned absence rate by department
-- Supports decision: Which departments require further investigation / workload review?

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
