-- R1: Annual overtime ranking and status by department
-- Supports decision: Should we redistribute workload between departments?

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