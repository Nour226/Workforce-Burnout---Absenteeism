-- Unplanned absences by weekday
-- Supports investigation of Monday / Friday effects
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