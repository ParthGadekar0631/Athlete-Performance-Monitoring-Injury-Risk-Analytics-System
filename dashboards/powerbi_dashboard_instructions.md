# Power BI Dashboard Instructions

## Connect the Data

1. Open Power BI Desktop.
2. Select **Get Data > Text/CSV**.
3. Choose `data/analytics/dashboard_export.csv`.
4. In Power Query, set `date` to Date and confirm numeric fields are Decimal Number or Whole Number.
5. Load the table and name it `Athlete Monitoring`.

## Page 1: Team Overview

Recommended visuals:

- Line chart: `date` vs average `workload_score`.
- Line chart: `date` vs average `readiness_score`.
- Card: count of distinct `player_id` where `risk_category` is Elevated or High.
- Clustered bar chart: `position` vs sum of `workload_spike_flag`.
- Histogram or column chart: distribution of `recovery_score`.

## Page 2: Player Monitoring

Add a slicer for `player_name`. Add line charts for:

- `workload_score`
- `acwr`
- `readiness_score`
- `soreness_rating`
- `sleep_hours`
- `injury_risk_score`

Use `date` as the shared x-axis.

## Page 3: Pitcher Workload

Add a page-level filter where `position` equals Pitcher. Build visuals for:

- Pitch count trend
- Throwing volume trend
- Velocity trend
- Recovery score trend
- Workload spike alerts by date and player

Use `session_type` as legend when comparing bullpen, game, and practice workloads.

## Page 4: Risk Alerts

Create a table filtered to Elevated and High risk categories. Include:

- Date
- Player
- Team
- Position
- Fatigue status
- Risk category
- Injury-risk score
- ACWR
- Recovery
- Sleep
- Soreness
- Workload spike flag

Recommended DAX reason-code measures can flag High ACWR, Low recovery, High soreness, Low sleep, Velocity decline, and Workload spike from the exported fields.
