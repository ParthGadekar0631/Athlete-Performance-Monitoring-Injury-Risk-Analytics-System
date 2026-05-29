from __future__ import annotations

from functools import lru_cache

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from src.config.settings import CLEAN_DATA_PATH, DASHBOARD_EXPORT_PATH, FEATURES_PATH, RISK_SCORES_PATH, DatabaseSettings


def get_engine():
    return create_engine(DatabaseSettings().sqlalchemy_url, pool_pre_ping=True)


def database_status() -> str:
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return "available"
    except SQLAlchemyError:
        return "unavailable"


def _read(path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@lru_cache(maxsize=8)
def sessions_df() -> pd.DataFrame:
    return _read(CLEAN_DATA_PATH)


@lru_cache(maxsize=8)
def features_df() -> pd.DataFrame:
    return _read(FEATURES_PATH)


@lru_cache(maxsize=8)
def risk_df() -> pd.DataFrame:
    return _read(RISK_SCORES_PATH)


@lru_cache(maxsize=8)
def dashboard_df() -> pd.DataFrame:
    return _read(DASHBOARD_EXPORT_PATH)


def clear_cache() -> None:
    sessions_df.cache_clear()
    features_df.cache_clear()
    risk_df.cache_clear()
    dashboard_df.cache_clear()


def records(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    clean = df.replace({pd.NA: None}).where(pd.notnull(df), None)
    return clean.to_dict(orient="records")


def players() -> pd.DataFrame:
    sessions = sessions_df()
    if sessions.empty:
        return pd.DataFrame(columns=["player_id", "player_name", "team", "position"])
    return sessions[["player_id", "player_name", "team", "position"]].drop_duplicates("player_id").sort_values("player_name")


def require_player(player_id: str) -> pd.Series:
    player_rows = players()
    match = player_rows[player_rows["player_id"] == player_id]
    if match.empty:
        raise KeyError(player_id)
    return match.iloc[0]
