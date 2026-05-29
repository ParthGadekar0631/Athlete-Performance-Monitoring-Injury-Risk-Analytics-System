from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.config.settings import RAW_DATA_PATH, ensure_data_directories
from src.utils.file_utils import write_csv
from src.utils.logger import get_logger

LOGGER = get_logger(__name__)

POSITIONS = [
    "Pitcher",
    "Catcher",
    "First Base",
    "Second Base",
    "Third Base",
    "Shortstop",
    "Left Field",
    "Center Field",
    "Right Field",
]
SESSION_TYPES = ["Game", "Practice", "Bullpen", "Strength Training", "Recovery", "Rest Day", "Travel Day"]
TEAMS = ["Brooklyn Bats", "Chicago Lakes", "Dallas Ropers", "Seattle Sound"]
FIRST_NAMES = [
    "Aaron", "Blake", "Carlos", "Dante", "Eli", "Felix", "Grant", "Hector", "Isaac", "Jalen",
    "Kai", "Luca", "Marco", "Nolan", "Owen", "Parker", "Quinn", "Rafael", "Silas", "Theo",
    "Victor", "Wes", "Xavier", "Yuri", "Zane", "Andre", "Benny", "Cole", "Diego", "Emil",
    "Finn", "Gabe", "Harvey", "Ivan", "Jonah", "Kenny", "Luis", "Miles", "Noah", "Oscar",
]
LAST_NAMES = [
    "Adams", "Bennett", "Castillo", "Diaz", "Ellis", "Foster", "Garcia", "Hayes", "Ibarra", "Johnson",
    "Kim", "Lopez", "Martinez", "Nguyen", "Ortiz", "Patel", "Reed", "Santos", "Turner", "Vargas",
]


def create_player_profiles(num_players: int = 32, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    positions = ["Pitcher"] * 11 + ["Catcher"] * 3 + POSITIONS[2:] * 3
    rng.shuffle(positions)
    records = []
    for idx in range(num_players):
        records.append(
            {
                "player_id": f"P{idx + 1:03d}",
                "player_name": f"{FIRST_NAMES[idx % len(FIRST_NAMES)]} {LAST_NAMES[(idx * 3) % len(LAST_NAMES)]}",
                "team": TEAMS[idx % len(TEAMS)],
                "position": positions[idx % len(positions)],
            }
        )
    return pd.DataFrame(records)


def choose_session(day_index: int, position: str, rng: np.random.Generator) -> str:
    weekday = day_index % 7
    if weekday == 0:
        return "Rest Day"
    if weekday == 4 and rng.random() < 0.28:
        return "Travel Day"
    if position == "Pitcher" and rng.random() < 0.22:
        return "Bullpen"
    if weekday in [2, 5, 6] and rng.random() < 0.72:
        return "Game"
    if rng.random() < 0.18:
        return "Strength Training"
    if rng.random() < 0.12:
        return "Recovery"
    return "Practice"


def generate_daily_record(
    player: pd.Series,
    current_date: date,
    day_index: int,
    fatigue_memory: float,
    rng: np.random.Generator,
) -> tuple[dict[str, object], float]:
    position = str(player["position"])
    session_type = choose_session(day_index, position, rng)
    is_pitcher = position == "Pitcher"

    base_workload = {
        "Game": 520,
        "Practice": 320,
        "Bullpen": 420,
        "Strength Training": 260,
        "Recovery": 110,
        "Rest Day": 35,
        "Travel Day": 95,
    }[session_type]
    workload = max(0, rng.normal(base_workload, 65))

    if is_pitcher:
        throwing = {
            "Game": rng.normal(115, 22),
            "Bullpen": rng.normal(75, 15),
            "Practice": rng.normal(48, 14),
            "Strength Training": rng.normal(18, 8),
            "Recovery": rng.normal(10, 5),
            "Rest Day": rng.normal(3, 3),
            "Travel Day": rng.normal(8, 5),
        }[session_type]
        pitch_count = {"Game": rng.normal(88, 20), "Bullpen": rng.normal(42, 12)}.get(session_type, rng.normal(5, 5))
        sprint = rng.normal(9 if session_type == "Game" else 5, 4)
    else:
        throwing = {
            "Game": rng.normal(48, 16),
            "Practice": rng.normal(38, 12),
            "Strength Training": rng.normal(10, 7),
            "Recovery": rng.normal(6, 4),
            "Rest Day": rng.normal(1, 2),
            "Travel Day": rng.normal(4, 3),
            "Bullpen": rng.normal(12, 5),
        }[session_type]
        pitch_count = rng.normal(0, 2)
        sprint = {
            "Game": rng.normal(24, 8),
            "Practice": rng.normal(18, 6),
            "Strength Training": rng.normal(7, 4),
            "Recovery": rng.normal(4, 3),
            "Rest Day": rng.normal(1, 1),
            "Travel Day": rng.normal(3, 2),
            "Bullpen": rng.normal(3, 2),
        }[session_type]

    fatigue_memory = max(0, fatigue_memory * 0.74 + workload / 820 + throwing / 260 - 0.3)
    if session_type in ["Rest Day", "Recovery"]:
        fatigue_memory = max(0, fatigue_memory - 0.55)

    sleep = rng.normal(7.7, 0.8) - (0.65 if session_type == "Travel Day" else 0) - fatigue_memory * 0.12
    soreness = np.clip(rng.normal(3.4 + fatigue_memory * 1.4 + workload / 420, 1.2), 1, 10)
    recovery = np.clip(rng.normal(84 - fatigue_memory * 7 - soreness * 2.0 + (sleep - 7) * 3, 6), 0, 100)
    avg_hr = np.clip(rng.normal(128 + workload / 24 + fatigue_memory * 2.5, 8), 70, 205)
    max_hr = np.clip(avg_hr + rng.normal(38, 9), avg_hr, 220)
    velocity = rng.normal(0.1, 0.45) - fatigue_memory * 0.08 - (0.35 if recovery < 58 else 0)
    readiness = np.clip(
        0.58 * recovery + 5.2 * sleep - 3.8 * soreness - workload / 35 - max(avg_hr - 150, 0) * 0.25 + 24,
        0,
        100,
    )
    risk_probability = 0.03
    risk_probability += 0.09 if workload > 620 else 0
    risk_probability += 0.11 if recovery < 60 else 0
    risk_probability += 0.08 if sleep < 6 else 0
    risk_probability += 0.1 if soreness > 7 else 0
    risk_probability += 0.08 if readiness < 65 else 0
    risk_probability += 0.07 if velocity < -0.6 else 0
    injury_flag = int(rng.random() < min(risk_probability, 0.72))

    record = {
        "player_id": player["player_id"],
        "player_name": player["player_name"],
        "team": player["team"],
        "position": position,
        "date": current_date.isoformat(),
        "session_type": session_type,
        "workload_score": round(float(workload), 1),
        "sprint_count": int(max(0, round(float(sprint)))),
        "throwing_volume": int(max(0, round(float(throwing)))),
        "pitch_count": int(max(0, round(float(pitch_count)))),
        "average_heart_rate": round(float(avg_hr), 1),
        "max_heart_rate": round(float(max_hr), 1),
        "recovery_score": round(float(recovery), 1),
        "sleep_hours": round(float(np.clip(sleep, 3.2, 11.5)), 1),
        "soreness_rating": round(float(soreness), 1),
        "velocity_trend": round(float(velocity), 2),
        "readiness_score": round(float(readiness), 1),
        "injury_flag": injury_flag,
    }
    return record, fatigue_memory


def inject_data_quality_issues(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 99)
    out = df.copy()
    duplicate_rows = out.sample(12, random_state=seed)
    out = pd.concat([out, duplicate_rows], ignore_index=True)

    for col in ["sleep_hours", "recovery_score", "workload_score", "session_type"]:
        idx = rng.choice(out.index, size=8, replace=False)
        out.loc[idx, col] = np.nan

    out.loc[rng.choice(out.index, size=5, replace=False), "workload_score"] = [-50, 1250, 1400, -20, 1120]
    out.loc[rng.choice(out.index, size=4, replace=False), "sleep_hours"] = [1.5, 15.0, 2.5, 13.2]
    out.loc[rng.choice(out.index, size=4, replace=False), "soreness_rating"] = [0, 12, -2, 15]
    out.loc[rng.choice(out.index, size=4, replace=False), "readiness_score"] = [-10, 130, 118, -5]

    non_pitchers = out[out["position"] != "Pitcher"].sample(8, random_state=seed + 1).index
    out.loc[non_pitchers, "pitch_count"] = rng.integers(35, 75, size=len(non_pitchers))
    rest_days = out[out["session_type"] == "Rest Day"].sample(7, random_state=seed + 2).index
    out.loc[rest_days, "workload_score"] = rng.integers(360, 650, size=len(rest_days))
    out.loc[rng.choice(out.index, size=3, replace=False), "position"] = "Designated Runner"
    return out.sample(frac=1, random_state=seed).reset_index(drop=True)


def generate_dataset(days: int = 100, players: int = 32, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profiles = create_player_profiles(players, seed)
    start_date = date.today() - timedelta(days=days - 1)
    rows = []
    for _, player in profiles.iterrows():
        fatigue_memory = float(rng.uniform(0.0, 1.3))
        for day_index in range(days):
            record, fatigue_memory = generate_daily_record(
                player, start_date + timedelta(days=day_index), day_index, fatigue_memory, rng
            )
            rows.append(record)
    return inject_data_quality_issues(pd.DataFrame(rows), seed=seed)


def main(output_path: Path = RAW_DATA_PATH) -> None:
    ensure_data_directories()
    LOGGER.info("Starting synthetic data generation")
    df = generate_dataset()
    write_csv(df, output_path)
    LOGGER.info("Wrote %s raw records to %s", len(df), output_path)


if __name__ == "__main__":
    main()
