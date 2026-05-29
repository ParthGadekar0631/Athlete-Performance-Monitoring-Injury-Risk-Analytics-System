from __future__ import annotations

import numpy as np
import pandas as pd


def add_fatigue_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add interpretable fatigue flags and status fields."""
    out = df.copy()
    out["low_recovery_flag"] = out["recovery_score"] < 60
    out["low_sleep_flag"] = out["sleep_hours"] < 6
    out["high_soreness_flag"] = out["soreness_rating"] > 7
    out["low_readiness_flag"] = out["readiness_score"] < 65
    out["velocity_decline_flag"] = out["velocity_trend_change"] < -0.4

    baseline_hr = out.groupby("player_id")["average_heart_rate"].transform("median")
    out["high_hr_flag"] = out["average_heart_rate"] > (baseline_hr + 10)

    warning_cols = [
        "low_recovery_flag",
        "low_sleep_flag",
        "high_soreness_flag",
        "low_readiness_flag",
        "workload_spike_flag",
        "velocity_decline_flag",
        "high_hr_flag",
    ]
    out["fatigue_warning_count"] = out[warning_cols].sum(axis=1)
    out["fatigue_flag"] = out["fatigue_warning_count"] >= 3

    conditions = [
        (out["workload_spike_flag"] & (out["low_recovery_flag"] | out["high_soreness_flag"] | out["low_readiness_flag"]))
        | (out["fatigue_warning_count"] >= 5),
        (out["acwr"] > 1.5) | (out["fatigue_warning_count"] >= 3),
        out["fatigue_warning_count"].between(1, 2),
    ]
    choices = ["High Risk", "Elevated Risk", "Monitor"]
    out["fatigue_status"] = np.select(conditions, choices, default="Normal")
    return out
