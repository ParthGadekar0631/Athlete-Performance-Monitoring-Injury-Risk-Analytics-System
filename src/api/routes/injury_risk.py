from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.database import records, require_player, risk_df

router = APIRouter(prefix="/injury-risk", tags=["injury risk"])


@router.get("/player/{player_id}")
def player_injury_risk(player_id: str):
    try:
        require_player(player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc
    df = risk_df()
    return records(df[df["player_id"] == player_id].sort_values("date"))


@router.get("/high")
def high_risk():
    df = risk_df()
    if df.empty:
        return []
    return records(df[df["risk_category"].isin(["Elevated", "High"])].sort_values(["date", "injury_risk_score"], ascending=[False, False]))


@router.get("/latest")
def latest_risk():
    df = risk_df()
    if df.empty:
        return []
    latest = df.sort_values("date").groupby("player_id", as_index=False).tail(1)
    return records(latest.sort_values("injury_risk_score", ascending=False))
