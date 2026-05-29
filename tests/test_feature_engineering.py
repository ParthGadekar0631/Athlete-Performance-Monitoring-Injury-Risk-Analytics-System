from __future__ import annotations

import pandas as pd

from src.config.settings import FEATURES_PATH
from src.processing.feature_engineering import engineer_features


def test_feature_engineering_outputs_required_columns(prepared_pipeline):
    df = engineer_features()
    for col in [
        "workload_7d_avg",
        "workload_28d_avg",
        "acwr",
        "workload_spike_flag",
        "fatigue_flag",
    ]:
        assert col in df.columns
    assert df["acwr"].notna().all()
    assert df["workload_spike_flag"].dtype == bool


def test_feature_file_written(prepared_pipeline):
    features = pd.read_csv(FEATURES_PATH)
    assert not features.empty
    assert {"fatigue_status", "injury_risk_score", "risk_category"}.issubset(features.columns)
