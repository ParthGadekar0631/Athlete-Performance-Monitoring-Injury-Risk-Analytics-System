from __future__ import annotations

import pytest

from src.analytics.injury_risk_model import generate_risk_scores
from src.analytics.player_reports import generate_player_report
from src.api.database import clear_cache
from src.data_generation.generate_synthetic_data import main as generate_main
from src.processing.clean_data import clean_dataset
from src.processing.feature_engineering import engineer_features
from src.validation.validate_data import validate_dataset


@pytest.fixture(scope="session", autouse=True)
def prepared_pipeline():
    generate_main()
    validate_dataset()
    clean_dataset()
    engineer_features()
    generate_risk_scores()
    generate_player_report()
    clear_cache()
    return True
