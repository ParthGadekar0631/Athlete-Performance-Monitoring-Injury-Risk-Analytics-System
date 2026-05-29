from __future__ import annotations

import pandas as pd

from src.validation.data_quality_rules import (
    duplicate_records,
    missing_required_columns,
    non_pitcher_high_pitch_count,
    numeric_range_issue,
)


def test_missing_required_columns_detected():
    df = pd.DataFrame({"player_id": ["P001"]})
    issue = missing_required_columns(df)
    assert issue.count > 0


def test_duplicate_records_detected():
    df = pd.DataFrame(
        {
            "player_id": ["P001", "P001"],
            "date": ["2026-01-01", "2026-01-01"],
            "session_type": ["Game", "Game"],
        }
    )
    assert duplicate_records(df).count == 2


def test_invalid_workload_detected():
    df = pd.DataFrame({"workload_score": [100, -1, 1200]})
    assert numeric_range_issue(df, "workload_score", 0, 1000, "High").count == 2


def test_invalid_sleep_hours_detected():
    df = pd.DataFrame({"sleep_hours": [7, 2.5, 13]})
    assert numeric_range_issue(df, "sleep_hours", 3, 12, "Medium").count == 2


def test_non_pitcher_high_pitch_count_detected():
    df = pd.DataFrame({"position": ["Shortstop", "Pitcher"], "pitch_count": [40, 90]})
    assert non_pitcher_high_pitch_count(df).count == 1
