from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_average(
    df: pd.DataFrame,
    value_col: str,
    window: int,
    group_col: str = "player_id",
) -> pd.Series:
    """Calculate player-level rolling averages ordered by date."""
    ordered = df.sort_values([group_col, "date"]).copy()
    values = (
        ordered.groupby(group_col)[value_col]
        .rolling(window=window, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    return values.reindex(ordered.index).reindex(df.index)


def calculate_acwr(acute: pd.Series, chronic: pd.Series) -> pd.Series:
    """Calculate ACWR safely, returning 0 when chronic workload is zero."""
    chronic_safe = chronic.replace(0, np.nan)
    return (acute / chronic_safe).replace([np.inf, -np.inf], np.nan).fillna(0).round(3)


def detect_workload_spikes(df: pd.DataFrame) -> pd.Series:
    """Flag workload spikes from daily load, ACWR, or throwing-volume jumps."""
    ordered = df.sort_values(["player_id", "date"]).copy()
    prev_throwing_7d = (
        ordered.groupby("player_id")["throwing_volume"]
        .shift(1)
        .rolling(window=7, min_periods=1)
        .mean()
    )
    daily_spike = ordered["workload_score"] > (ordered["workload_7d_avg"].replace(0, np.nan) * 1.5)
    acwr_spike = ordered["acwr"] > 1.5
    throwing_spike = ordered["throwing_volume"] > (prev_throwing_7d.replace(0, np.nan) * 1.6)
    spikes = (daily_spike | acwr_spike | throwing_spike).fillna(False)
    return spikes.reindex(df.index).fillna(False)


def player_workload_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["player_id", "player_name", "position"], as_index=False)
        .agg(
            avg_workload=("workload_score", "mean"),
            total_workload=("workload_score", "sum"),
            workload_spike_count=("workload_spike_flag", "sum"),
            avg_acwr=("acwr", "mean"),
            latest_date=("date", "max"),
        )
        .round(2)
    )


def team_workload_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["team", "date"], as_index=False)
        .agg(
            avg_workload=("workload_score", "mean"),
            avg_readiness=("readiness_score", "mean"),
            workload_spikes=("workload_spike_flag", "sum"),
            high_soreness_count=("high_soreness_flag", "sum"),
        )
        .round(2)
    )


def position_workload_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["position", "date"], as_index=False)
        .agg(
            avg_workload=("workload_score", "mean"),
            avg_acwr=("acwr", "mean"),
            avg_throwing=("throwing_volume", "mean"),
            avg_sprint_count=("sprint_count", "mean"),
        )
        .round(2)
    )


def acwr_category(acwr: float) -> str:
    if acwr < 0.8:
        return "Undertraining / Low Load"
    if acwr <= 1.3:
        return "Normal"
    if acwr <= 1.5:
        return "Monitor"
    return "Elevated Workload Risk"
