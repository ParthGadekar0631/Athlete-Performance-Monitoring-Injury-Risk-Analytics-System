from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.database import database_status, sessions_df
from src.api.routes import dashboard, injury_risk, players, readiness, workload

app = FastAPI(
    title="Baseball Athlete Performance Monitoring & Injury Risk Analytics System",
    version="0.1.0",
    description="Synthetic baseball workload, readiness, and injury-risk analytics API.",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(players.router)
app.include_router(workload.router)
app.include_router(readiness.router)
app.include_router(injury_risk.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "project": "Baseball Athlete Performance Monitoring & Injury Risk Analytics System",
        "status": "running",
        "dashboard": "/dashboard",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    data_status = "available" if not sessions_df().empty else "missing"
    return {"api_status": "ok", "database_status": database_status(), "data_status": data_status}
