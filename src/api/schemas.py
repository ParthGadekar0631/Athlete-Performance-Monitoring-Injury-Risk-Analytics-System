from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class PlayerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id: str
    player_name: str
    team: str
    position: str


class HealthSchema(BaseModel):
    api_status: str
    database_status: str
    data_status: str


class RecordSchema(BaseModel):
    data: dict[str, Any] | list[dict[str, Any]]
