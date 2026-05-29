from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.database import features_df, players, records, require_player, risk_df, sessions_df
from src.api.schemas import PlayerSchema

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerSchema])
def get_players():
    return records(players())


@router.get("/{player_id}")
def get_player(player_id: str):
    try:
        return require_player(player_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc


@router.get("/{player_id}/summary")
def get_player_summary(player_id: str):
    try:
        player = require_player(player_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown player_id: {player_id}") from exc

    sessions = sessions_df()
    features = features_df()
    risks = risk_df()
    latest_session = sessions[sessions["player_id"] == player_id].sort_values("date").tail(1)
    latest_feature = features[features["player_id"] == player_id].sort_values("date").tail(1)
    latest_risk = risks[risks["player_id"] == player_id].sort_values("date").tail(1)
    summary = {"player": player}
    if not latest_session.empty:
        row = latest_session.iloc[0]
        summary.update(
            {
                "date": row["date"],
                "latest_workload": row["workload_score"],
                "latest_readiness": row["readiness_score"],
                "latest_recovery": row["recovery_score"],
            }
        )
    if not latest_feature.empty:
        row = latest_feature.iloc[0]
        summary.update({"fatigue_status": row["fatigue_status"], "acwr": row["acwr"]})
    if not latest_risk.empty:
        row = latest_risk.iloc[0]
        summary.update({"injury_risk_score": row["injury_risk_score"], "risk_category": row["risk_category"]})
    return summary
