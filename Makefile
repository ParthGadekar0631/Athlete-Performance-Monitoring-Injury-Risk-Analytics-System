.PHONY: install generate-data validate clean-data features model reports load-db api test docker-up pipeline

install:
	pip install -r requirements.txt

generate-data:
	python -m src.data_generation.generate_synthetic_data

validate:
	python -m src.validation.validate_data

clean-data:
	python -m src.processing.clean_data

features:
	python -m src.processing.feature_engineering

model:
	python -m src.analytics.injury_risk_model

reports:
	python -m src.analytics.player_reports

load-db:
	python -m src.ingestion.load_to_postgres

api:
	uvicorn src.api.main:app --reload

test:
	pytest

docker-up:
	docker-compose up --build

pipeline: generate-data validate clean-data features model reports
