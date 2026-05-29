from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.api.database import dashboard_df, records

router = APIRouter(tags=["dashboard"])
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@router.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(STATIC_DIR / "dashboard.html")


@router.get("/dashboard/data")
def dashboard_data():
    df = dashboard_df()
    if df.empty:
        return {"records": [], "players": [], "teams": [], "positions": [], "date_range": {"min": None, "max": None}}

    players = (
        df[["player_id", "player_name", "team", "position"]]
        .drop_duplicates("player_id")
        .sort_values("player_name")
        .to_dict(orient="records")
    )
    return {
        "records": records(df),
        "players": players,
        "teams": sorted(df["team"].dropna().unique().tolist()),
        "positions": sorted(df["position"].dropna().unique().tolist()),
        "date_range": {"min": str(df["date"].min()), "max": str(df["date"].max())},
    }
