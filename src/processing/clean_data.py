from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config.settings import CLEAN_DATA_PATH, QUALITY_REPORT_PATH, RAW_DATA_PATH, ensure_data_directories
from src.utils.file_utils import read_csv_checked, write_csv
from src.utils.logger import get_logger
from src.validation.data_quality_rules import VALID_POSITIONS, VALID_SESSION_TYPES

LOGGER = get_logger(__name__)

NUMERIC_RANGES = {
    "workload_score": (0, 1000),
    "sprint_count": (0, 60),
    "throwing_volume": (0, 220),
    "pitch_count": (0, 130),
    "average_heart_rate": (50, 210),
    "max_heart_rate": (70, 230),
    "recovery_score": (0, 100),
    "sleep_hours": (3, 12),
    "soreness_rating": (1, 10),
    "velocity_trend": (-5, 5),
    "readiness_score": (0, 100),
    "injury_flag": (0, 1),
}


def _impute_numeric(df: pd.DataFrame, column: str) -> int:
    missing_before = int(df[column].isna().sum())
    grouped = df.groupby(["position", "session_type"], dropna=False)[column].transform("median")
    overall = df[column].median()
    df[column] = df[column].fillna(grouped).fillna(overall)
    return missing_before


def clean_dataset(input_path: Path = RAW_DATA_PATH, output_path: Path = CLEAN_DATA_PATH) -> pd.DataFrame:
    ensure_data_directories()
    LOGGER.info("Starting cleaning for %s", input_path)
    df = read_csv_checked(input_path)
    original_count = len(df)
    imputed_count = 0

    df.columns = [col.strip() for col in df.columns]
    for col in ["player_id", "player_name", "team", "position", "session_type"]:
        df[col] = df[col].astype("string").str.strip()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["player_id", "player_name", "team", "position", "date"])
    df = df[df["position"].isin(VALID_POSITIONS)]
    df["session_type"] = df["session_type"].where(df["session_type"].isin(VALID_SESSION_TYPES), pd.NA)
    mode_session = df["session_type"].mode(dropna=True)
    session_fill = mode_session.iloc[0] if not mode_session.empty else "Practice"
    imputed_count += int(df["session_type"].isna().sum())
    df["session_type"] = df["session_type"].fillna(session_fill)

    for col, (low, high) in NUMERIC_RANGES.items():
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[(df[col] < low) | (df[col] > high), col] = pd.NA
        imputed_count += _impute_numeric(df, col)
        df[col] = df[col].clip(low, high)

    df.loc[df["position"] != "Pitcher", "pitch_count"] = df.loc[df["position"] != "Pitcher", "pitch_count"].clip(0, 15)
    rest_mask = df["session_type"] == "Rest Day"
    df.loc[rest_mask, "workload_score"] = df.loc[rest_mask, "workload_score"].clip(0, 150)
    df.loc[rest_mask, ["sprint_count", "throwing_volume", "pitch_count"]] = df.loc[
        rest_mask, ["sprint_count", "throwing_volume", "pitch_count"]
    ].clip(lower=0)

    int_cols = ["sprint_count", "throwing_volume", "pitch_count", "injury_flag"]
    for col in int_cols:
        df[col] = df[col].round().astype(int)

    df = df.sort_values(["player_id", "date", "session_type"])
    df = df.drop_duplicates(["player_id", "date", "session_type"], keep="first")
    removed_count = original_count - len(df)
    df["date"] = df["date"].dt.date.astype(str)
    write_csv(df, output_path)

    if QUALITY_REPORT_PATH.exists():
        report = json.loads(QUALITY_REPORT_PATH.read_text(encoding="utf-8"))
    else:
        report = {"total_records_processed": original_count}
    report["cleaned_record_count"] = int(len(df))
    report["removed_record_count"] = int(removed_count)
    report["imputed_value_count"] = int(imputed_count)
    QUALITY_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    LOGGER.info("Wrote %s cleaned records to %s", len(df), output_path)
    return df


def main() -> None:
    clean_dataset()


if __name__ == "__main__":
    main()
