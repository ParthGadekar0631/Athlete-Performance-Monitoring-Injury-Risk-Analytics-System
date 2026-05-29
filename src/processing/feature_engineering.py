from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.analytics.fatigue_detection import add_fatigue_indicators
from src.analytics.workload_metrics import acwr_category, calculate_acwr, detect_workload_spikes
from src.config.settings import (
    CLEAN_DATA_PATH,
    DASHBOARD_EXPORT_PATH,
    FEATURES_PATH,
    READINESS_SUMMARY_PATH,
    WORKLOAD_TRENDS_PATH,
    ensure_data_directories,
)
from src.utils.file_utils import read_csv_checked, write_csv
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


def _rolling(df: pd.DataFrame, column: str, window: int) -> pd.Series:
    ordered = df.sort_values(["player_id", "date"]).copy()
    rolled = (
        ordered.groupby("player_id")[column]
        .rolling(window=window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    return rolled.reindex(df.index)


def _trend(df: pd.DataFrame, column: str, periods: int = 3) -> pd.Series:
    ordered = df.sort_values(["player_id", "date"]).copy()
    trended = ordered.groupby("player_id")[column].diff(periods=periods).fillna(0)
    return trended.reindex(df.index)


def _transparent_risk_score(df: pd.DataFrame) -> pd.Series:
    score = pd.Series(0, index=df.index, dtype=float)
    score += np.where(df["acwr"] > 1.5, 25, 0)
    score += np.where(df["recovery_score"] < 60, 20, 0)
    score += np.where(df["sleep_hours"] < 6, 15, 0)
    score += np.where(df["soreness_rating"] > 7, 15, 0)
    score += np.where(df["readiness_score"] < 65, 15, 0)
    score += np.where(df["velocity_trend_change"] < -0.4, 10, 0)
    score += np.where(df["workload_spike_flag"], 10, 0)
    baseline_hr = df.groupby("player_id")["average_heart_rate"].transform("median")
    score += np.where(df["average_heart_rate"] > baseline_hr + 10, 10, 0)
    return score.clip(0, 100).round(1)


def _risk_category(score: float) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "Elevated"
    return "High"


def engineer_features(input_path: Path = CLEAN_DATA_PATH, output_path: Path = FEATURES_PATH) -> pd.DataFrame:
    ensure_data_directories()
    LOGGER.info("Starting feature engineering for %s", input_path)
    df = read_csv_checked(input_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["player_id", "date"]).reset_index(drop=True)

    df["workload_7d_avg"] = _rolling(df, "workload_score", 7).round(2)
    df["workload_28d_avg"] = _rolling(df, "workload_score", 28).round(2)
    df["acwr"] = calculate_acwr(df["workload_7d_avg"], df["workload_28d_avg"])
    df["throwing_7d_avg"] = _rolling(df, "throwing_volume", 7).round(2)
    df["sprint_7d_avg"] = _rolling(df, "sprint_count", 7).round(2)
    df["soreness_7d_avg"] = _rolling(df, "soreness_rating", 7).round(2)
    df["sleep_7d_avg"] = _rolling(df, "sleep_hours", 7).round(2)
    df["recovery_trend"] = _trend(df, "recovery_score").round(2)
    df["readiness_trend"] = _trend(df, "readiness_score").round(2)
    df["velocity_trend_change"] = _trend(df, "velocity_trend").round(2)
    df["workload_spike_flag"] = detect_workload_spikes(df)
    df = add_fatigue_indicators(df)
    df["acwr_category"] = df["acwr"].apply(acwr_category)
    df["injury_risk_score"] = _transparent_risk_score(df)
    df["risk_category"] = df["injury_risk_score"].apply(_risk_category)
    df["date"] = df["date"].dt.date.astype(str)

    write_csv(df, output_path)
    LOGGER.info("Wrote %s feature records to %s", len(df), output_path)

    readiness = (
        df.sort_values("date")
        .groupby(["player_id", "player_name", "team", "position"], as_index=False)
        .tail(1)[
            [
                "player_id",
                "player_name",
                "team",
                "position",
                "date",
                "readiness_score",
                "recovery_score",
                "sleep_hours",
                "soreness_rating",
                "fatigue_status",
                "injury_risk_score",
                "risk_category",
            ]
        ]
    )
    write_csv(readiness, READINESS_SUMMARY_PATH)

    workload = df[
        [
            "player_id",
            "player_name",
            "team",
            "position",
            "date",
            "session_type",
            "workload_score",
            "workload_7d_avg",
            "workload_28d_avg",
            "acwr",
            "throwing_volume",
            "throwing_7d_avg",
            "sprint_count",
            "sprint_7d_avg",
            "workload_spike_flag",
        ]
    ]
    write_csv(workload, WORKLOAD_TRENDS_PATH)
    write_csv(df, DASHBOARD_EXPORT_PATH)
    return df


def main() -> None:
    engineer_features()


if __name__ == "__main__":
    main()
