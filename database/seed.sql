INSERT INTO data_quality_issues (player_id, date, issue_type, issue_description, severity)
VALUES
    (NULL, NULL, 'methodology_note', 'Synthetic data includes controlled duplicate, missing, and out-of-range values so validation and cleaning can be demonstrated.', 'Low')
ON CONFLICT DO NOTHING;
