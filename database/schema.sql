CREATE TABLE IF NOT EXISTS players (
    player_id TEXT PRIMARY KEY,
    player_name TEXT NOT NULL,
    team TEXT NOT NULL,
    position TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS athlete_sessions (
    session_id BIGSERIAL PRIMARY KEY,
    player_id TEXT NOT NULL REFERENCES players(player_id),
    date DATE NOT NULL,
    session_type TEXT NOT NULL,
    workload_score NUMERIC,
    sprint_count INTEGER,
    throwing_volume INTEGER,
    pitch_count INTEGER,
    average_heart_rate NUMERIC,
    max_heart_rate NUMERIC,
    recovery_score NUMERIC,
    sleep_hours NUMERIC,
    soreness_rating NUMERIC,
    velocity_trend NUMERIC,
    readiness_score NUMERIC,
    injury_flag INTEGER,
    UNIQUE (player_id, date, session_type)
);

CREATE TABLE IF NOT EXISTS athlete_features (
    feature_id BIGSERIAL PRIMARY KEY,
    player_id TEXT NOT NULL REFERENCES players(player_id),
    date DATE NOT NULL,
    workload_7d_avg NUMERIC,
    workload_28d_avg NUMERIC,
    acwr NUMERIC,
    throwing_7d_avg NUMERIC,
    sprint_7d_avg NUMERIC,
    soreness_7d_avg NUMERIC,
    sleep_7d_avg NUMERIC,
    recovery_trend NUMERIC,
    readiness_trend NUMERIC,
    workload_spike_flag BOOLEAN,
    fatigue_flag BOOLEAN,
    low_recovery_flag BOOLEAN,
    high_soreness_flag BOOLEAN,
    fatigue_status TEXT,
    UNIQUE (player_id, date)
);

CREATE TABLE IF NOT EXISTS injury_risk_scores (
    risk_id BIGSERIAL PRIMARY KEY,
    player_id TEXT NOT NULL REFERENCES players(player_id),
    date DATE NOT NULL,
    injury_risk_score NUMERIC NOT NULL,
    risk_category TEXT NOT NULL,
    model_version TEXT NOT NULL,
    UNIQUE (player_id, date, model_version)
);

CREATE TABLE IF NOT EXISTS data_quality_issues (
    issue_id BIGSERIAL PRIMARY KEY,
    player_id TEXT,
    date DATE,
    issue_type TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    severity TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_player_date ON athlete_sessions(player_id, date);
CREATE INDEX IF NOT EXISTS idx_features_player_date ON athlete_features(player_id, date);
CREATE INDEX IF NOT EXISTS idx_risk_category ON injury_risk_scores(risk_category, date);
