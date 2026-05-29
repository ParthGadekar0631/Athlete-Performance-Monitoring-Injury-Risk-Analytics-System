from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS = [
    "player_id",
    "player_name",
    "team",
    "position",
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
VALID_POSITIONS = {
    "Pitcher",
    "Catcher",
    "First Base",
    "Second Base",
    "Third Base",
    "Shortstop",
    "Left Field",
    "Center Field",
    "Right Field",
}
VALID_SESSION_TYPES = {"Game", "Practice", "Bullpen", "Strength Training", "Recovery", "Rest Day", "Travel Day"}


@dataclass(frozen=True)
class QualityIssue:
    rule: str
    severity: str
    count: int
    description: str

    def as_dict(self) -> dict[str, object]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "count": int(self.count),
            "description": self.description,
        }


def missing_required_columns(df: pd.DataFrame) -> QualityIssue:
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    return QualityIssue("missing_required_columns", "High", len(missing), ", ".join(missing))


def duplicate_records(df: pd.DataFrame) -> QualityIssue:
    if not {"player_id", "date", "session_type"}.issubset(df.columns):
        return QualityIssue("duplicate_records", "High", 0, "Cannot check duplicates without key columns.")
    count = int(df.duplicated(["player_id", "date", "session_type"], keep=False).sum())
    return QualityIssue("duplicate_records", "Medium", count, "Duplicate player/date/session records.")


def missing_values(df: pd.DataFrame) -> dict[str, int]:
    return {col: int(count) for col, count in df.isna().sum().items() if count > 0}


def invalid_dates(df: pd.DataFrame) -> QualityIssue:
    if "date" not in df:
        return QualityIssue("invalid_dates", "High", 0, "Date column missing.")
    count = int(pd.to_datetime(df["date"], errors="coerce").isna().sum())
    return QualityIssue("invalid_dates", "High", count, "Rows with invalid dates.")


def numeric_range_issue(df: pd.DataFrame, column: str, min_value: float, max_value: float, severity: str) -> QualityIssue:
    if column not in df:
        return QualityIssue(f"{column}_range", severity, 0, f"{column} missing.")
    values = pd.to_numeric(df[column], errors="coerce")
    count = int(((values < min_value) | (values > max_value)).sum())
    return QualityIssue(
        f"{column}_range",
        severity,
        count,
        f"{column} outside expected range {min_value}-{max_value}.",
    )


def categorical_issue(df: pd.DataFrame, column: str, valid_values: set[str]) -> QualityIssue:
    if column not in df:
        return QualityIssue(f"invalid_{column}", "High", 0, f"{column} missing.")
    count = int((~df[column].dropna().isin(valid_values)).sum())
    return QualityIssue(f"invalid_{column}", "High", count, f"Invalid {column} values.")


def non_pitcher_high_pitch_count(df: pd.DataFrame) -> QualityIssue:
    if not {"position", "pitch_count"}.issubset(df.columns):
        return QualityIssue("non_pitcher_high_pitch_count", "High", 0, "Required columns missing.")
    pitch_count = pd.to_numeric(df["pitch_count"], errors="coerce")
    count = int(((df["position"] != "Pitcher") & (pitch_count > 15)).sum())
    return QualityIssue(
        "non_pitcher_high_pitch_count",
        "High",
        count,
        "Non-pitchers with unrealistic pitch counts above 15.",
    )


def rest_day_high_workload(df: pd.DataFrame) -> QualityIssue:
    if not {"session_type", "workload_score"}.issubset(df.columns):
        return QualityIssue("rest_day_high_workload", "Medium", 0, "Required columns missing.")
    workload = pd.to_numeric(df["workload_score"], errors="coerce")
    count = int(((df["session_type"] == "Rest Day") & (workload > 150)).sum())
    return QualityIssue("rest_day_high_workload", "Medium", count, "Rest days with workload above 150.")


def game_day_missing_workload(df: pd.DataFrame) -> QualityIssue:
    if not {"session_type", "workload_score"}.issubset(df.columns):
        return QualityIssue("game_day_missing_workload", "High", 0, "Required columns missing.")
    count = int(((df["session_type"] == "Game") & (df["workload_score"].isna())).sum())
    return QualityIssue("game_day_missing_workload", "High", count, "Game rows missing workload score.")


def missing_consecutive_days(df: pd.DataFrame) -> QualityIssue:
    if not {"player_id", "date"}.issubset(df.columns):
        return QualityIssue("player_logs_missing_consecutive_days", "Low", 0, "Required columns missing.")
    work = df[["player_id", "date"]].copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work = work.dropna().drop_duplicates()
    gaps = 0
    for _, group in work.sort_values("date").groupby("player_id"):
        diffs = group["date"].diff().dt.days.dropna()
        gaps += int((diffs > 1).sum())
    return QualityIssue("player_logs_missing_consecutive_days", "Low", gaps, "Player logs with date gaps.")


def run_quality_rules(df: pd.DataFrame) -> list[QualityIssue]:
    issues = [
        missing_required_columns(df),
        duplicate_records(df),
        invalid_dates(df),
        numeric_range_issue(df, "workload_score", 0, 1000, "High"),
        numeric_range_issue(df, "sprint_count", 0, 60, "Medium"),
        numeric_range_issue(df, "throwing_volume", 0, 220, "Medium"),
        numeric_range_issue(df, "pitch_count", 0, 130, "High"),
        numeric_range_issue(df, "average_heart_rate", 50, 210, "High"),
        numeric_range_issue(df, "max_heart_rate", 70, 230, "High"),
        numeric_range_issue(df, "sleep_hours", 3, 12, "Medium"),
        numeric_range_issue(df, "soreness_rating", 1, 10, "Medium"),
        numeric_range_issue(df, "recovery_score", 0, 100, "Medium"),
        numeric_range_issue(df, "readiness_score", 0, 100, "Medium"),
        categorical_issue(df, "session_type", VALID_SESSION_TYPES),
        categorical_issue(df, "position", VALID_POSITIONS),
        non_pitcher_high_pitch_count(df),
        rest_day_high_workload(df),
        game_day_missing_workload(df),
        missing_consecutive_days(df),
    ]
    return issues
