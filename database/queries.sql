-- Daily workload by player
SELECT p.player_name, s.date, s.session_type, s.workload_score, s.throwing_volume, s.pitch_count
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
ORDER BY p.player_name, s.date;

-- Top players by workload spike count
SELECT p.player_name, p.position, COUNT(*) AS workload_spike_days
FROM athlete_features f
JOIN players p ON p.player_id = f.player_id
WHERE f.workload_spike_flag = TRUE
GROUP BY p.player_name, p.position
ORDER BY workload_spike_days DESC;

-- Players with ACWR above 1.5
SELECT p.player_name, p.position, f.date, f.acwr
FROM athlete_features f
JOIN players p ON p.player_id = f.player_id
WHERE f.acwr > 1.5
ORDER BY f.date DESC, f.acwr DESC;

-- Players with low readiness
SELECT p.player_name, s.date, s.readiness_score, s.recovery_score, s.soreness_rating
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
WHERE s.readiness_score < 65
ORDER BY s.date DESC, s.readiness_score ASC;

-- Players with high soreness
SELECT p.player_name, s.date, s.soreness_rating, s.workload_score
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
WHERE s.soreness_rating > 7
ORDER BY s.date DESC, s.soreness_rating DESC;

-- Pitcher workload trend
SELECT p.player_name, s.date, s.session_type, s.pitch_count, s.throwing_volume, s.workload_score, f.acwr
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
LEFT JOIN athlete_features f ON f.player_id = s.player_id AND f.date = s.date
WHERE p.position = 'Pitcher'
ORDER BY p.player_name, s.date;

-- Team-level readiness average
SELECT p.team, s.date, ROUND(AVG(s.readiness_score), 2) AS avg_readiness
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
GROUP BY p.team, s.date
ORDER BY s.date, p.team;

-- Injury-risk score by player
SELECT p.player_name, p.position, r.date, r.injury_risk_score, r.risk_category
FROM injury_risk_scores r
JOIN players p ON p.player_id = r.player_id
ORDER BY r.date DESC, r.injury_risk_score DESC;

-- Recovery trend by position
SELECT p.position, f.date, ROUND(AVG(f.recovery_trend), 2) AS avg_recovery_trend
FROM athlete_features f
JOIN players p ON p.player_id = f.player_id
GROUP BY p.position, f.date
ORDER BY f.date, p.position;

-- Last 14 days player monitoring summary
SELECT p.player_name, p.team, p.position, s.date, s.workload_score, f.acwr, s.readiness_score,
       s.recovery_score, s.soreness_rating, f.fatigue_status, r.injury_risk_score, r.risk_category
FROM athlete_sessions s
JOIN players p ON p.player_id = s.player_id
LEFT JOIN athlete_features f ON f.player_id = s.player_id AND f.date = s.date
LEFT JOIN injury_risk_scores r ON r.player_id = s.player_id AND r.date = s.date
WHERE s.date >= CURRENT_DATE - INTERVAL '14 days'
ORDER BY s.date DESC, p.player_name;
