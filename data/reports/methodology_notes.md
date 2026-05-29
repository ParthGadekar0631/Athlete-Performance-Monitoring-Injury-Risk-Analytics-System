# Methodology Notes

## Synthetic Data Assumptions

This project uses synthetic daily player monitoring data for 32 baseball athletes over at least 90 days. The data is designed to resemble a performance science workflow, not to reproduce a real club's internal data.

Player profiles include team, position, and daily session type. Session workloads vary by baseball role:

- Pitchers receive larger throwing volume and pitch count on game and bullpen days.
- Position players receive larger sprint counts on game and practice days.
- Rest days and recovery days carry lower workload.
- Travel days reduce sleep and recovery in the simulation.

The raw dataset intentionally includes duplicate records, missing values, invalid categories, unrealistic values, and inconsistent logs so the validation and cleaning pipeline can demonstrate realistic data quality controls.

## Baseball Workload Assumptions

Workload score is a synthetic composite representing external and internal load. It is influenced by session type, throwing volume, sprint count, heart rate, and accumulated fatigue. It is bounded to 0-1000 after cleaning.

Throwing volume is a broad count-like measure of throws, not a biomechanical measurement. Pitch count is meaningful for pitchers and should be zero or very low for non-pitchers.

## ACWR Calculation

Acute-to-Chronic Workload Ratio is calculated as:

```text
acute_workload = 7-day rolling workload average
chronic_workload = 28-day rolling workload average
ACWR = acute_workload / chronic_workload
```

Division by zero is handled safely. Risk interpretation:

- ACWR below 0.8: Undertraining / low load
- ACWR 0.8 to 1.3: Normal
- ACWR above 1.3 to 1.5: Monitor
- ACWR above 1.5: Elevated workload risk

## Fatigue Detection Rules

Fatigue status is generated from interpretable warning signs:

- Recovery score below 60
- Sleep below 6 hours
- Soreness rating above 7
- Readiness score below 65
- Workload spike flag
- Declining velocity trend
- Average heart rate more than 10 bpm above player baseline

Statuses are Normal, Monitor, Elevated Risk, and High Risk.

## Injury-Risk Score Logic

The 0-100 injury-risk score combines transparent rules and a Random Forest classifier trained on the synthetic `injury_flag`.

Rule-based weights:

- ACWR above 1.5: +25
- Recovery score below 60: +20
- Sleep below 6 hours: +15
- Soreness above 7: +15
- Readiness below 65: +15
- Velocity trend declining: +10
- Throwing or workload spike: +10
- Heart rate above baseline: +10

Risk categories:

- 0-30: Low
- 31-60: Moderate
- 61-80: Elevated
- 81-100: High

## Model Limitations

The model is trained on generated labels from synthetic data. Metrics describe performance against the simulation, not real injury prediction skill. Real deployment would require athlete consent, validated measurements, clinical governance, longitudinal history, and domain review by medical and performance staff.

## Ethical Note

This is not medical advice and must not be used for real athlete medical decisions. It is a portfolio simulation for sports analytics, data engineering, and performance reporting workflows.
