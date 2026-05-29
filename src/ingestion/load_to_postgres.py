from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from src.config.settings import (
    CLEAN_DATA_PATH,
    FEATURES_PATH,
    PROJECT_ROOT,
    QUALITY_REPORT_PATH,
    RISK_SCORES_PATH,
    DatabaseSettings,
)
from src.utils.file_utils import read_csv_checked
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


def _execute_sql_file(engine, path: Path) -> None:
    with engine.begin() as conn:
        conn.execute(text(path.read_text(encoding="utf-8")))


def _load_quality_issues() -> pd.DataFrame:
    if not QUALITY_REPORT_PATH.exists():
        return pd.DataFrame(columns=["player_id", "date", "issue_type", "issue_description", "severity"])
    report = json.loads(QUALITY_REPORT_PATH.read_text(encoding="utf-8"))
    rows = []
    for issue in report.get("invalid_records_by_rule", []):
        if issue.get("count", 0):
            rows.append(
                {
                    "player_id": None,
                    "date": None,
                    "issue_type": issue["rule"],
                    "issue_description": f"{issue['description']} Count: {issue['count']}",
                    "severity": issue["severity"],
                }
            )
    return pd.DataFrame(rows)


def load_to_postgres() -> None:
    LOGGER.info("Starting PostgreSQL load")
    settings = DatabaseSettings()
    engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _execute_sql_file(engine, PROJECT_ROOT / "database" / "schema.sql")

        sessions = read_csv_checked(CLEAN_DATA_PATH)
        features = read_csv_checked(FEATURES_PATH)
        risks = read_csv_checked(RISK_SCORES_PATH)

        players = sessions[["player_id", "player_name", "team", "position"]].drop_duplicates("player_id")
        session_cols = [
            "player_id",
            "date",
            "session_type",
            "workload_score",
            "sprint_count",
            "throwing_volume",
            "pitch_count",
            "average_heart_rate",
            "max_heart_rate",
            "recovery_score",
            "sleep_hours",
            "soreness_rating",
            "velocity_trend",
            "readiness_score",
            "injury_flag",
        ]
        feature_cols = [
            "player_id",
            "date",
            "workload_7d_avg",
            "workload_28d_avg",
            "acwr",
            "throwing_7d_avg",
            "sprint_7d_avg",
            "soreness_7d_avg",
            "sleep_7d_avg",
            "recovery_trend",
            "readiness_trend",
            "workload_spike_flag",
            "fatigue_flag",
            "low_recovery_flag",
            "high_soreness_flag",
            "fatigue_status",
        ]
        risk_cols = ["player_id", "date", "injury_risk_score", "risk_category", "model_version"]

        with engine.begin() as conn:
            conn.execute(text("TRUNCATE data_quality_issues, injury_risk_scores, athlete_features, athlete_sessions, players RESTART IDENTITY CASCADE"))
        players.to_sql("players", engine, if_exists="append", index=False)
        sessions[session_cols].to_sql("athlete_sessions", engine, if_exists="append", index=False)
        features[feature_cols].to_sql("athlete_features", engine, if_exists="append", index=False)
        risks[risk_cols].to_sql("injury_risk_scores", engine, if_exists="append", index=False)
        issues = _load_quality_issues()
        if not issues.empty:
            issues.to_sql("data_quality_issues", engine, if_exists="append", index=False)
        LOGGER.info("Loaded players=%s sessions=%s features=%s risks=%s", len(players), len(sessions), len(features), len(risks))
    except SQLAlchemyError as exc:
        LOGGER.error("Database load failed: %s", exc)
        raise RuntimeError("Could not load PostgreSQL. Check database env vars and server status.") from exc
    finally:
        engine.dispose()


def main() -> None:
    load_to_postgres()


if __name__ == "__main__":
    main()
