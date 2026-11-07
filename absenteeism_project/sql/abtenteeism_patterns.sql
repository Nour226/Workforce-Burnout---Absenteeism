--R6:
WITH employee_absence_summary AS (
    -- 1. Calcul des jours d'absences cumulés par employé
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
    
    -- Le VRAI nombre d'employés uniques par département
    COUNT(DISTINCT e.employee_id) AS total_employees,
    
    -- Jours d'absences totaux du département
    COALESCE(SUM(eas.total_absence_days), 0) AS total_absence_days,
    
    -- Jours d'absences non planifiées
    COALESCE(SUM(eas.unplanned_absence_days), 0) AS unplanned_absence_days,
    
    -- Jours d'absences non justifiées
    COALESCE(SUM(eas.unjustified_absence_days), 0) AS unjustified_absence_days,
    
    -- Pourcentage exact d'absences non planifiées
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

SELECT * FROM absences 


















--R7:
SELECT 
    a.weekday,
    CASE a.weekday
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



--R8
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
LEFT JOIN absences a ON e.employee_id = a.employee_id
GROUP BY d.dept_id, d.dept_name
ORDER BY unplanned_absence_rate_pct DESC;


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
WHERE a.absence_type = 'Unplanned' -- On se concentre uniquement sur l'absentéisme imprévu
GROUP BY d.dept_id, d.dept_name, a.reason
ORDER BY d.dept_name ASC, total_lost_days DESC;




