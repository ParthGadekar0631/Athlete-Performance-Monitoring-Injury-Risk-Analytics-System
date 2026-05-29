from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config.settings import QUALITY_REPORT_PATH, RAW_DATA_PATH, ensure_data_directories
from src.utils.file_utils import read_csv_checked
from src.utils.logger import get_logger
from src.validation.data_quality_rules import missing_values, run_quality_rules

LOGGER = get_logger(__name__)


def validate_dataset(input_path: Path = RAW_DATA_PATH, output_path: Path = QUALITY_REPORT_PATH) -> dict[str, object]:
    ensure_data_directories()
    LOGGER.info("Starting validation for %s", input_path)
    df = read_csv_checked(input_path)
    issues = run_quality_rules(df)
    missing_by_column = missing_values(df)
    invalid_record_count = int(sum(issue.count for issue in issues if issue.severity in {"High", "Medium"}))
    duplicate_count = next((issue.count for issue in issues if issue.rule == "duplicate_records"), 0)

    report = {
        "total_records_processed": int(len(df)),
        "duplicate_records": int(duplicate_count),
        "missing_values_by_column": missing_by_column,
        "invalid_records_by_rule": [issue.as_dict() for issue in issues],
        "severity_summary": {
            "Low": int(sum(issue.count for issue in issues if issue.severity == "Low")),
            "Medium": int(sum(issue.count for issue in issues if issue.severity == "Medium")),
            "High": int(sum(issue.count for issue in issues if issue.severity == "High")),
        },
        "cleaned_record_count": None,
        "removed_record_count": None,
        "imputed_value_count": int(sum(missing_by_column.values())),
        "validation_note": "Cleaning step fills cleaned/removed counts after processing.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    LOGGER.info(
        "Validation complete: %s records, %s duplicate-key rows, %s medium/high issue flags",
        len(df),
        duplicate_count,
        invalid_record_count,
    )
    print(json.dumps(report["severity_summary"], indent=2))
    return report


def main() -> None:
    validate_dataset()


if __name__ == "__main__":
    main()
