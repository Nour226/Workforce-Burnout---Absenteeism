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

