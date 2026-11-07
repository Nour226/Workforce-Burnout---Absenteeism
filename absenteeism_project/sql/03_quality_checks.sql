-- =====================================================================
-- 03_quality_checks.sql  |  Data-quality report (Role A)
-- Every "violations" column should be 0. Run with:  psql -f sql/03_quality_checks.sql
-- =====================================================================

\echo '--- 1. Row counts -------------------------------------------------'
SELECT 'departments' AS tbl, COUNT(*) AS n FROM departments
UNION ALL SELECT 'employees',       COUNT(*) FROM employees
UNION ALL SELECT 'weekly_workload', COUNT(*) FROM weekly_workload
UNION ALL SELECT 'absences',        COUNT(*) FROM absences;

\echo '--- 2. Referential integrity (violations) -----------------------'
SELECT 'employees without a department' AS check_name, COUNT(*) AS violations
FROM employees e LEFT JOIN departments d USING (dept_id) WHERE d.dept_id IS NULL
UNION ALL
SELECT 'employees whose manager does not exist', COUNT(*)
FROM employees e LEFT JOIN employees m ON m.employee_id = e.manager_id
WHERE e.manager_id IS NOT NULL AND m.employee_id IS NULL
UNION ALL
SELECT 'manager in another department', COUNT(*)
FROM employees e JOIN employees m ON m.employee_id = e.manager_id WHERE m.dept_id <> e.dept_id
UNION ALL
SELECT 'workload rows without employee', COUNT(*)
FROM weekly_workload w LEFT JOIN employees e USING (employee_id) WHERE e.employee_id IS NULL
UNION ALL
SELECT 'absence rows without employee', COUNT(*)
FROM absences a LEFT JOIN employees e USING (employee_id) WHERE e.employee_id IS NULL;

\echo '--- 3. Domain and consistency rules (violations) ----------------'
SELECT 'absence on a weekend' AS check_name, COUNT(*) AS violations
FROM absences WHERE EXTRACT(ISODOW FROM absence_date) > 5
UNION ALL
SELECT 'absence before hire date', COUNT(*)
FROM absences a JOIN employees e USING (employee_id) WHERE a.absence_date < e.hire_date
UNION ALL
SELECT 'duplicate employee/day in absences', COUNT(*) FROM (
    SELECT employee_id, absence_date FROM absences GROUP BY 1, 2 HAVING COUNT(*) > 1) x
UNION ALL
SELECT 'duplicate employee/week in weekly_workload', COUNT(*) FROM (
    SELECT employee_id, week_start FROM weekly_workload GROUP BY 1, 2 HAVING COUNT(*) > 1) x
UNION ALL
SELECT 'weekly hours outside 20-80 h', COUNT(*)
FROM weekly_workload WHERE hours_worked NOT BETWEEN 20 AND 80
UNION ALL
SELECT 'planned leave marked unjustified', COUNT(*)
FROM absences WHERE absence_type = 'Planned leave' AND NOT is_justified;

\echo '--- 4. NULL counts per column (should be 0 except employees.manager_id) ---'
SELECT 'employees.manager_id' AS col, COUNT(*) FILTER (WHERE manager_id IS NULL) AS nulls FROM employees
UNION ALL SELECT 'employees.dept_id', COUNT(*) FILTER (WHERE dept_id IS NULL) FROM employees
UNION ALL SELECT 'weekly_workload.hours_worked', COUNT(*) FILTER (WHERE hours_worked IS NULL) FROM weekly_workload
UNION ALL SELECT 'absences.reason', COUNT(*) FILTER (WHERE reason IS NULL) FROM absences;

\echo '--- 5. Known irregularity: missing employee-weeks (documented, not an error) ---'
SELECT COUNT(*) AS expected_rows,
       (SELECT COUNT(*) FROM weekly_workload) AS actual_rows,
       ROUND(100.0 * (1 - (SELECT COUNT(*) FROM weekly_workload)::numeric / COUNT(*)), 2) AS missing_pct
FROM employees e
CROSS JOIN (SELECT DISTINCT week_start FROM weekly_workload) w;

\echo '--- 6. Distribution sanity -----------------------------------------'
SELECT absence_type, COUNT(*) AS days, COUNT(DISTINCT employee_id) AS employees FROM absences GROUP BY 1;
SELECT reason, COUNT(*) AS days FROM absences WHERE absence_type = 'Unplanned' GROUP BY 1 ORDER BY 2 DESC;
SELECT d.dept_name, COUNT(*) AS employees, ROUND(AVG(overtime_flag::int) * 100, 1) AS pct_overtime_yes
FROM employees e JOIN departments d USING (dept_id) GROUP BY 1 ORDER BY 2 DESC;
