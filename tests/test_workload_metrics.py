from __future__ import annotations

import pandas as pd

from src.analytics.workload_metrics import calculate_acwr, detect_workload_spikes


def test_acwr_calculated_safely():
    acute = pd.Series([10, 20, 30])
    chronic = pd.Series([0, 20, 15])
    acwr = calculate_acwr(acute, chronic)
    assert acwr.iloc[0] == 0
    assert acwr.iloc[1] == 1
    assert acwr.iloc[2] == 2


def test_workload_spike_flag_generated():
    df = pd.DataFrame(
        {
            "player_id": ["P001"] * 3,
            "date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "workload_score": [100, 110, 400],
            "workload_7d_avg": [100, 105, 160],
            "acwr": [1.0, 1.1, 1.6],
            "throwing_volume": [20, 20, 70],
        }
    )
    spikes = detect_workload_spikes(df)
    assert bool(spikes.iloc[-1]) is True
