from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "athlete_monitoring_raw.csv"
CLEAN_DATA_PATH = DATA_DIR / "processed" / "athlete_monitoring_clean.csv"
ANALYTICS_DIR = DATA_DIR / "analytics"
REPORTS_DIR = DATA_DIR / "reports"
FEATURES_PATH = ANALYTICS_DIR / "athlete_features.csv"
RISK_SCORES_PATH = ANALYTICS_DIR / "injury_risk_scores.csv"
READINESS_SUMMARY_PATH = ANALYTICS_DIR / "player_readiness_summary.csv"
WORKLOAD_TRENDS_PATH = ANALYTICS_DIR / "workload_trends.csv"
DASHBOARD_EXPORT_PATH = ANALYTICS_DIR / "dashboard_export.csv"
QUALITY_REPORT_PATH = REPORTS_DIR / "data_quality_report.json"


@dataclass(frozen=True)
class DatabaseSettings:
    host: str = os.getenv("DATABASE_HOST", "localhost")
    port: int = int(os.getenv("DATABASE_PORT", "5432"))
    name: str = os.getenv("DATABASE_NAME", "baseball_analytics")
    user: str = os.getenv("DATABASE_USER", "postgres")
    password: str = os.getenv("DATABASE_PASSWORD", "postgres")

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


def ensure_data_directories() -> None:
    for path in [
        DATA_DIR / "raw",
        DATA_DIR / "processed",
        ANALYTICS_DIR,
        REPORTS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
