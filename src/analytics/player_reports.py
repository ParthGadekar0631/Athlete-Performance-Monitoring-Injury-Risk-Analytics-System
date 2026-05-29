from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import FEATURES_PATH, REPORTS_DIR, RISK_SCORES_PATH, ensure_data_directories
from src.utils.file_utils import read_csv_checked
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)


def _alert_reasons(row: pd.Series) -> list[str]:
    reasons = []
    if row.get("acwr", 0) > 1.5:
        reasons.append("High ACWR")
    if row.get("recovery_score", 100) < 60:
        reasons.append("Low recovery")
    if row.get("soreness_rating", 0) > 7:
        reasons.append("High soreness")
    if row.get("sleep_hours", 10) < 6:
        reasons.append("Low sleep")
    if row.get("velocity_trend_change", 0) < -0.4:
        reasons.append("Velocity decline")
    if bool(row.get("workload_spike_flag", False)):
        reasons.append("Workload spike")
    return reasons or ["No major alerts"]


def generate_player_report(player_id: str | None = None, output_path: Path | None = None) -> Path:
    ensure_data_directories()
    features = read_csv_checked(FEATURES_PATH)
    risks = read_csv_checked(RISK_SCORES_PATH) if RISK_SCORES_PATH.exists() else pd.DataFrame()
    if player_id is None:
        latest_risky = features.sort_values(["injury_risk_score", "date"], ascending=[False, False]).iloc[0]
        player_id = str(latest_risky["player_id"])

    player_df = features[features["player_id"] == player_id].sort_values("date")
    if player_df.empty:
        raise ValueError(f"Unknown player_id: {player_id}")

    latest = player_df.iloc[-1].copy()
    if not risks.empty:
        risk_latest = risks[risks["player_id"] == player_id].sort_values("date").tail(1)
        if not risk_latest.empty:
            latest["injury_risk_score"] = risk_latest.iloc[0]["injury_risk_score"]
            latest["risk_category"] = risk_latest.iloc[0]["risk_category"]

    recent = player_df.tail(14)
    alerts = _alert_reasons(latest)
    output_path = output_path or REPORTS_DIR / "player_report_sample.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = f"""# Player Monitoring Report: {latest['player_name']}

## Player Information

- Player ID: {latest['player_id']}
- Team: {latest['team']}
- Position: {latest['position']}
- Report date: {latest['date']}

## Recent Workload Trend

- Latest workload score: {latest['workload_score']}
- 7-day workload average: {latest['workload_7d_avg']}
- 28-day workload average: {latest['workload_28d_avg']}
- ACWR: {latest['acwr']} ({latest['acwr_category']})
- Workload spike flag: {bool(latest['workload_spike_flag'])}

## Recovery and Readiness

- Latest recovery score: {latest['recovery_score']}
- Recovery trend versus three sessions ago: {latest['recovery_trend']}
- Latest readiness score: {latest['readiness_score']}
- Readiness trend versus three sessions ago: {latest['readiness_trend']}
- Sleep hours: {latest['sleep_hours']}
- Soreness rating: {latest['soreness_rating']}

## Fatigue and Injury-Risk Indicators

- Fatigue status: {latest['fatigue_status']}
- Injury-risk score: {latest['injury_risk_score']}
- Risk category: {latest['risk_category']}
- Key alerts: {', '.join(alerts)}

## Last 14 Days Snapshot

| Date | Session | Workload | ACWR | Readiness | Recovery | Soreness | Risk |
|---|---|---:|---:|---:|---:|---:|---:|
"""
    for _, row in recent.iterrows():
        report += (
            f"| {row['date']} | {row['session_type']} | {row['workload_score']} | {row['acwr']} | "
            f"{row['readiness_score']} | {row['recovery_score']} | {row['soreness_rating']} | "
            f"{row['injury_risk_score']} |\n"
        )

    report += """
## Coaching / Staff Review Notes

- Review workload spikes alongside planned game, bullpen, and travel context before changing training plans.
- For Elevated or High risk days, coordinate performance, strength, coaching, and athletic training review.
- This report is a sports analytics simulation and is not medical advice.
"""
    output_path.write_text(report, encoding="utf-8")
    LOGGER.info("Wrote sample player report to %s", output_path)
    return output_path


def main() -> None:
    generate_player_report()


if __name__ == "__main__":
    main()
