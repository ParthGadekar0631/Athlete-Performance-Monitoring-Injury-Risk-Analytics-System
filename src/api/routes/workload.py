from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.database import features_df, records, require_player

router = APIRouter(prefix="/workload", tags=["workload"])


@router.get("/player/{player_id}")
def player_workload(player_id: str):
    try:
        require_player(player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc
    df = features_df()
    cols = [
        "date",
        "session_type",
        "workload_score",
        "workload_7d_avg",
        "workload_28d_avg",
        "acwr",
        "throwing_volume",
        "pitch_count",
        "sprint_count",
        "workload_spike_flag",
    ]
    return records(df[df["player_id"] == player_id][cols].sort_values("date"))


@router.get("/spikes")
def workload_spikes():
    df = features_df()
    if df.empty:
        return []
    cols = ["player_id", "player_name", "team", "position", "date", "workload_score", "acwr", "workload_spike_flag"]
    return records(df[df["workload_spike_flag"].astype(bool)][cols].sort_values(["date", "acwr"], ascending=[False, False]))


@router.get("/team-summary")
def team_summary():
    df = features_df()
    if df.empty:
        return []
    summary = (
        df.groupby(["team", "position", "date"], as_index=False)
        .agg(
            avg_workload=("workload_score", "mean"),
            avg_readiness=("readiness_score", "mean"),
            avg_acwr=("acwr", "mean"),
            workload_spikes=("workload_spike_flag", "sum"),
        )
        .round(2)
        .sort_values(["date", "team", "position"])
    )
    return records(summary)
