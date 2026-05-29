from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.database import features_df, records, require_player

router = APIRouter(prefix="/readiness", tags=["readiness"])


@router.get("/player/{player_id}")
def player_readiness(player_id: str):
    try:
        require_player(player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc
    df = features_df()
    cols = ["date", "readiness_score", "readiness_trend", "recovery_score", "sleep_hours", "soreness_rating", "fatigue_status"]
    return records(df[df["player_id"] == player_id][cols].sort_values("date"))


@router.get("/low")
def low_readiness(threshold: float = 65):
    df = features_df()
    if df.empty:
        return []
    cols = ["player_id", "player_name", "team", "position", "date", "readiness_score", "recovery_score", "fatigue_status"]
    return records(df[df["readiness_score"] < threshold][cols].sort_values(["date", "readiness_score"], ascending=[False, True]))
