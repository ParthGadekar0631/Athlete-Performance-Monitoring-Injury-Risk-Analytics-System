from __future__ import annotations

import pandas as pd

from src.data_generation.generate_synthetic_data import generate_dataset


def test_data_generation_columns_exist():
    df = generate_dataset(days=90, players=25, seed=7)
    expected = {
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
    }
    assert expected.issubset(df.columns)


def test_data_generation_at_least_90_days_and_multiple_positions():
    df = generate_dataset(days=90, players=25, seed=8)
    dates = pd.to_datetime(df["date"], errors="coerce")
    assert dates.nunique() >= 90
    assert df["position"].nunique() > 5
    assert "injury_flag" in df.columns
