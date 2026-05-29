# Tableau Dashboard Instructions

## Connect the Data

1. Open Tableau Desktop.
2. Select **Text file**.
3. Choose `data/analytics/dashboard_export.csv`.
4. Confirm `date` is recognized as a Date field.
5. Convert boolean fields such as `workload_spike_flag`, `fatigue_flag`, `low_recovery_flag`, and `high_soreness_flag` to dimensions if Tableau imports them as text.

## Page 1: Team Overview

Create these sheets:

- Average workload by date: line chart with `date` on Columns and AVG(`workload_score`) on Rows.
- Average readiness by date: line chart with `date` and AVG(`readiness_score`).
- Number of high-risk players: count distinct `player_id` filtered to `risk_category` in Elevated or High.
- Workload spikes by position: bar chart with `position` and SUM(`workload_spike_flag`).
- Recovery score distribution: histogram of `recovery_score`.

Combine the sheets into a dashboard named **Team Overview**.

## Page 2: Player Monitoring

Add a `player_name` filter and create:

- Workload trend line using `workload_score`.
- ACWR trend line using `acwr`.
- Readiness trend line using `readiness_score`.
- Soreness trend line using `soreness_rating`.
- Sleep trend line using `sleep_hours`.
- Injury-risk score trend using `injury_risk_score`.

Use synchronized date axes where possible.

## Page 3: Pitcher Workload

Filter `position` to Pitcher. Create trend charts for:

- `pitch_count`
- `throwing_volume`
- `velocity_trend`
- `recovery_score`
- Workload spike alerts using `workload_spike_flag`

Add `session_type` as color to distinguish game, bullpen, practice, and recovery days.

## Page 4: Risk Alerts

Create a table with:

- `date`
- `player_name`
- `team`
- `position`
- `fatigue_status`
- `risk_category`
- `injury_risk_score`
- `acwr`
- `recovery_score`
- `sleep_hours`
- `soreness_rating`
- `workload_spike_flag`

Filter to `risk_category` Elevated or High. Add calculated reason-code fields such as High ACWR, Low recovery, High soreness, Low sleep, Velocity decline, and Workload spike.
