# Baseball Athlete Performance Monitoring & Injury Risk Analytics System

Professional portfolio project simulating a baseball performance analytics platform for workload monitoring, recovery tracking, readiness analysis, data quality validation, PostgreSQL storage, FastAPI access, and Tableau/Power BI exports.

## Sports Analytics Problem

Baseball staff need repeatable ways to monitor player workload, throwing volume, sprint exposure, recovery, soreness, sleep, and readiness across a long season. Sudden workload spikes, poor recovery, and declining readiness can inform coaching and performance staff review.

This project matters for baseball operations because it connects data engineering, quality control, interpretable analytics, and coach-ready reporting in one reproducible workflow.

## Tech Stack

Python 3.11+, Pandas, NumPy, Scikit-learn, SQLAlchemy, PostgreSQL, FastAPI, Uvicorn, Pydantic, pytest, python-dotenv, Docker, Docker Compose, GitHub Actions, Tableau/Power BI CSV exports.

## Architecture

```text
Synthetic Generator
    -> Raw CSV with intentional data quality issues
    -> Validation rules and JSON quality report
    -> Cleaning and standardization
    -> Rolling workload, ACWR, fatigue, readiness, and risk features
    -> Injury-risk model scores
    -> PostgreSQL tables + FastAPI endpoints + dashboard CSV exports
```

## Folder Structure

```text
baseball-athlete-performance-analytics/
├── data/                  # raw, processed, analytics exports, reports
├── database/              # PostgreSQL schema and analyst SQL
├── src/                   # pipeline, analytics, API, ingestion code
├── dashboards/            # Tableau and Power BI build instructions
├── notebooks/             # exploratory notebook
├── tests/                 # pytest coverage
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Dataset

The generator creates 100 days of player-level records for 32 synthetic players. Fields include player metadata, session type, workload score, sprint count, throwing volume, pitch count, average and max heart rate, recovery score, sleep hours, soreness rating, velocity trend, readiness score, and synthetic injury flag.

Positions include Pitcher, Catcher, First Base, Second Base, Third Base, Shortstop, Left Field, Center Field, and Right Field. Session types include Game, Practice, Bullpen, Strength Training, Recovery, Rest Day, and Travel Day.

## Data Quality Rules

Validation checks missing fields, duplicate player/date/session records, invalid dates, numeric ranges, invalid positions and session types, non-pitchers with high pitch counts, rest days with high workload, game days missing workload, and missing consecutive player logs. The report is saved to `data/reports/data_quality_report.json`.

## Feature Engineering

The feature pipeline calculates 7-day and 28-day workload averages, ACWR, rolling throwing volume, rolling sprint count, rolling soreness, rolling sleep, recovery trend, readiness trend, velocity trend change, workload spike flags, fatigue flags, and transparent injury-risk score fields.

## ACWR Methodology

```text
ACWR = 7-day rolling workload average / 28-day rolling workload average
```

Interpretation:

- Below 0.8: Undertraining / low load
- 0.8 to 1.3: Normal range
- Above 1.3 to 1.5: Monitor
- Above 1.5: Elevated workload risk

## Injury-Risk Scoring

The project creates a 0-100 risk score using transparent weighted rules and a Random Forest classifier trained on the synthetic `injury_flag`.

Risk factors include high ACWR, low recovery, low sleep, high soreness, low readiness, velocity decline, workload or throwing spike, and elevated heart rate versus player baseline.

Risk categories:

- 0-30: Low
- 31-60: Moderate
- 61-80: Elevated
- 81-100: High

This is not a clinical or medical model.

## API Endpoints

Run locally with:

```bash
uvicorn src.api.main:app --reload
```

Endpoints:

- `GET /`
- `GET /health`
- `GET /players`
- `GET /players/{player_id}`
- `GET /players/{player_id}/summary`
- `GET /workload/player/{player_id}`
- `GET /workload/spikes`
- `GET /workload/team-summary`
- `GET /readiness/player/{player_id}`
- `GET /readiness/low?threshold=65`
- `GET /injury-risk/player/{player_id}`
- `GET /injury-risk/high`
- `GET /injury-risk/latest`

Example requests:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/players
curl http://127.0.0.1:8000/players/P001/summary
curl http://127.0.0.1:8000/injury-risk/latest
```

Swagger documentation is available at `http://127.0.0.1:8000/docs`.

Read-only dashboard:

```bash
python -m uvicorn src.api.main:app --reload
```

Open `http://127.0.0.1:8000/dashboard`.

Hosted GitHub Pages dashboard:

```text
https://parthgadekar0631.github.io/Athlete-Performance-Monitoring-Injury-Risk-Analytics-System/
```

The hosted version is static and reads `docs/dashboard_export.csv` directly in the browser.

## Run Locally

```bash
pip install -r requirements.txt
python -m src.data_generation.generate_synthetic_data
python -m src.validation.validate_data
python -m src.processing.clean_data
python -m src.processing.feature_engineering
python -m src.analytics.injury_risk_model
python -m src.analytics.player_reports
pytest
uvicorn src.api.main:app --reload
```

Makefile shortcuts:

```bash
make install
make generate-data
make validate
make clean-data
make features
make model
make reports
make test
make api
```

## PostgreSQL

Copy `.env.example` to `.env` and update values if needed:

```text
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=baseball_analytics
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```

Load data:

```bash
python -m src.ingestion.load_to_postgres
```

## Docker

```bash
docker-compose up --build
```

The Compose stack starts PostgreSQL and the FastAPI app.

## Dashboard Usage

Use `data/analytics/dashboard_export.csv` in Tableau or Power BI. Build four pages:

- Team Overview
- Player Monitoring
- Pitcher Workload
- Risk Alerts

Instructions are documented in `dashboards/tableau_dashboard_instructions.md` and `dashboards/powerbi_dashboard_instructions.md`.

The project also includes a built-in read-only web dashboard served by FastAPI at `/dashboard`. It uses the same `dashboard_export.csv` data and provides filters for player, team, position, risk category, and date range.

## Example Output Screenshots

Add screenshots after building dashboards:

- `docs/images/team-overview.png`
- `docs/images/player-monitoring.png`
- `docs/images/pitcher-workload.png`
- `docs/images/risk-alerts.png`

## Testing

```bash
pytest
```

Tests cover data generation, validation rules, feature engineering, and FastAPI endpoints.

## Limitations and Assumptions

This is a synthetic portfolio simulation. It does not use real athlete biometric data and should not be used for medical decisions. ACWR and fatigue rules are simplified for demonstration. Real club deployment would require validated sensors, staff review, security controls, privacy governance, and longitudinal injury history.

## Future Improvements

- Add orchestration with Airflow or Prefect.
- Add warehouse modeling with dbt.
- Add role-based API authentication.
- Add interactive Plotly charts.
- Add model registry and drift monitoring.
- Add more granular pitcher-specific recovery and throwing stress features.

## Resume Bullet Section

Baseball Athlete Performance Monitoring & Injury Risk Analytics System  
Personal Project | Python, SQL, Scikit-learn, Tableau, PostgreSQL

- Built athlete monitoring pipeline to clean and analyze workload, recovery, and performance data across player-level time series.
- Designed data quality checks for missing sessions, abnormal workload spikes, duplicate records, and inconsistent player logs.
- Created injury-risk indicators using rolling averages, workload ratios, fatigue trends, and recovery-score changes.
- Built Tableau-ready dashboard exports to help coaches review player readiness, workload trends, and performance anomalies.
- Documented methods, assumptions, data definitions, and versioned analysis workflows for reproducible performance reporting.
