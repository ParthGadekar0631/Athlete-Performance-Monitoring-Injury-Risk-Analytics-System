from __future__ import annotations

from pathlib import Path

import pandas as pd


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")


def read_csv_checked(path: Path) -> pd.DataFrame:
    require_file(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"CSV file is empty: {path}")
    return df


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
