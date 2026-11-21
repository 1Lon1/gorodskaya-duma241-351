.PHONY: test lint audit check migrate migration-check backup restore-check

test:
	mkdir -p reports
	pytest -q --junitxml=reports/pytest.xml

lint:
	mkdir -p reports
	ruff check backend tests migrations scripts --output-format json --output-file reports/ruff.json

audit:
	mkdir -p reports
	pip-audit -r backend/requirements.txt --format json --output reports/pip-audit.json

migrate:
	DATABASE_URL=sqlite:///./ci_migration.db alembic upgrade head

migration-check:
	DATABASE_URL=sqlite:///./ci_migration.db alembic upgrade head
	DATABASE_URL=sqlite:///./ci_migration.db alembic check

backup:
	python scripts/backup_db.py

restore-check: backup
	python scripts/restore_test.py

check: lint test audit migration-check restore-check
