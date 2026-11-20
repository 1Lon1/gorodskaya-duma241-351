import os
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    source = Path(
        os.environ.get("DATABASE_FILE", "ci_migration.db")
    )
    backup_dir = Path(
        os.environ.get("BACKUP_DIR", "backups")
    )

    if not source.is_file():
        print(f"Database not found: {source}", file=sys.stderr)
        sys.exit(1)

    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime(
        "%Y%m%d_%H%M%S"
    )
    backup_file = backup_dir / f"backup_{timestamp}.db"

    try:
        with sqlite3.connect(source) as source_db:
            with sqlite3.connect(backup_file) as backup_db:
                source_db.backup(backup_db)

        with sqlite3.connect(backup_file) as check_db:
            result = check_db.execute(
                "PRAGMA integrity_check"
            ).fetchone()

        if result is None or result[0] != "ok":
            raise RuntimeError(
                f"Backup integrity check failed: {result}"
            )

        print(f"Backup created: {backup_file}")
        print("Integrity check: OK")

    except Exception:
        backup_file.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    main()
