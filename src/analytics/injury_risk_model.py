from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.config.settings import DASHBOARD_EXPORT_PATH, FEATURES_PATH, READINESS_SUMMARY_PATH, RISK_SCORES_PATH, ensure_data_directories
from src.utils.file_utils import read_csv_checked, write_csv
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)
MODEL_VERSION = "synthetic-rf-v1"

MODEL_FEATURES = [
    "workload_score",
    "sprint_count",
    "throwing_volume",
    "pitch_count",
    "average_heart_rate",
    "recovery_score",
    "sleep_hours",
    "soreness_rating",
    "readiness_score",
    "velocity_trend",
    "workload_7d_avg",
    "workload_28d_avg",
    "acwr",
    "throwing_7d_avg",
    "sprint_7d_avg",
    "soreness_7d_avg",
    "sleep_7d_avg",
    "workload_spike_flag",
    "fatigue_flag",
    "low_recovery_flag",
    "high_soreness_flag",
]


def score_category(score: float) -> str:
    if score <= 30:
        return "Low"
    if score <= 60:
        return "Moderate"
    if score <= 80:
        return "Elevated"
    return "High"


def rule_based_risk_score(df: pd.DataFrame) -> pd.Series:
    """Create a transparent 0-100 risk score using documented staff-facing rules."""
    score = pd.Series(0, index=df.index, dtype=float)
    score += np.where(df["acwr"] > 1.5, 25, 0)
    score += np.where(df["recovery_score"] < 60, 20, 0)
    score += np.where(df["sleep_hours"] < 6, 15, 0)
    score += np.where(df["soreness_rating"] > 7, 15, 0)
    score += np.where(df["readiness_score"] < 65, 15, 0)
    score += np.where(df["velocity_trend_change"] < -0.4, 10, 0)
    score += np.where((df["workload_spike_flag"]) | (df["throwing_volume"] > df["throwing_7d_avg"] * 1.6), 10, 0)
    baseline_hr = df.groupby("player_id")["average_heart_rate"].transform("median")
    score += np.where(df["average_heart_rate"] > baseline_hr + 10, 10, 0)
    return score.clip(0, 100).round(1)


def train_model(df: pd.DataFrame) -> tuple[RandomForestClassifier | None, dict[str, float]]:
    if df["injury_flag"].nunique() < 2 or len(df) < 50:
        LOGGER.warning("Insufficient class balance or records for model training; using rule-based scores only.")
        return None, {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}

    x = df[MODEL_FEATURES].fillna(0).astype(float)
    y = df["injury_flag"].astype(int)
    stratify = y if y.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=stratify
    )
    model = RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, predictions)), 3),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 3),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 3),
        "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 3),
    }
    return model, metrics


def generate_risk_scores(input_path: Path = FEATURES_PATH, output_path: Path = RISK_SCORES_PATH) -> pd.DataFrame:
    ensure_data_directories()
    LOGGER.info("Starting injury risk model pipeline")
    df = read_csv_checked(input_path)
    for col in ["workload_spike_flag", "fatigue_flag", "low_recovery_flag", "high_soreness_flag"]:
        df[col] = df[col].astype(bool).astype(int)

    model, metrics = train_model(df)
    rule_score = rule_based_risk_score(df)
    if model is not None:
        model_prob = model.predict_proba(df[MODEL_FEATURES].fillna(0).astype(float))[:, 1] * 100
        final_score = (0.55 * rule_score + 0.45 * model_prob).clip(0, 100).round(1)
    else:
        final_score = rule_score

    risk_df = df[["player_id", "player_name", "team", "position", "date"]].copy()
    risk_df["injury_risk_score"] = final_score
    risk_df["risk_category"] = risk_df["injury_risk_score"].apply(score_category)
    risk_df["model_version"] = MODEL_VERSION
    risk_df["model_accuracy"] = metrics["accuracy"]
    risk_df["model_precision"] = metrics["precision"]
    risk_df["model_recall"] = metrics["recall"]
    risk_df["model_f1"] = metrics["f1"]
    risk_df["model_note"] = (
        "Sports analytics simulation only. Not a clinical or medical injury prediction model."
    )
    write_csv(risk_df, output_path)
    if DASHBOARD_EXPORT_PATH.exists():
        dashboard = pd.read_csv(DASHBOARD_EXPORT_PATH)
        dashboard = dashboard.drop(columns=["injury_risk_score", "risk_category"], errors="ignore")
        dashboard = dashboard.merge(
            risk_df[["player_id", "date", "injury_risk_score", "risk_category"]],
            on=["player_id", "date"],
            how="left",
        )
        write_csv(dashboard, DASHBOARD_EXPORT_PATH)
    if READINESS_SUMMARY_PATH.exists():
        summary = pd.read_csv(READINESS_SUMMARY_PATH)
        latest_scores = risk_df.sort_values("date").groupby("player_id", as_index=False).tail(1)
        summary = summary.drop(columns=["injury_risk_score", "risk_category"], errors="ignore")
        summary = summary.merge(
            latest_scores[["player_id", "injury_risk_score", "risk_category"]],
            on="player_id",
            how="left",
        )
        write_csv(summary, READINESS_SUMMARY_PATH)
    (output_path.parent / "model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    LOGGER.info("Wrote %s risk score records to %s", len(risk_df), output_path)
    return risk_df


def main() -> None:
    generate_risk_scores()


if __name__ == "__main__":
    main()
