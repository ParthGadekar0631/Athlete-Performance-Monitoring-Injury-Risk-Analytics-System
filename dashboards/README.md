# Dashboard Guide

Use `data/analytics/dashboard_export.csv` as the single Tableau or Power BI source. It contains player metadata, daily workload, recovery, readiness, rolling workload features, ACWR, fatigue flags, and injury-risk scores.

A built-in read-only web dashboard is also available after starting FastAPI:

```bash
python -m uvicorn src.api.main:app --reload
```

Open `http://127.0.0.1:8000/dashboard`.

Recommended dashboard pages:

- Team Overview: workload, readiness, high-risk counts, workload spikes by position, recovery distribution.
- Player Monitoring: filter by player and trend workload, ACWR, readiness, soreness, sleep, and injury-risk score.
- Pitcher Workload: pitch count, throwing volume, velocity trend, recovery score, and spike alerts.
- Risk Alerts: player-days flagged as Elevated Risk or High Risk with reason-code fields inferred from ACWR, recovery, soreness, sleep, velocity, and workload spike flags.
