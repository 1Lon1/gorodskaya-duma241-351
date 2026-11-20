.PHONY: test lint check migrate migration-check backup restore-check

test:
	pytest -q

lint:
	ruff check backend tests migrations scripts

migrate:
	DATABASE_URL=sqlite:///./ci_migration.db alembic upgrade head

migration-check:
	DATABASE_URL=sqlite:///./ci_migration.db alembic upgrade head
	DATABASE_URL=sqlite:///./ci_migration.db alembic check
backup:
	python scripts/backup_db.py

restore-check: backup
	python scripts/restore_test.py

check: lint test migration-check restore-check
