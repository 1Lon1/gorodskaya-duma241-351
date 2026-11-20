import sqlite3
import sys
from pathlib import Path


def main() -> None:
    backup_dir = Path("backups")
    restore_dir = Path("restore_test")

    backups = sorted(backup_dir.glob("backup_*.db"))

    if not backups:
        print("No backup files found", file=sys.stderr)
        sys.exit(1)

    backup_file = backups[-1]
    restore_dir.mkdir(parents=True, exist_ok=True)

    restored_file = restore_dir / "restored.db"
    restored_file.unlink(missing_ok=True)

    with sqlite3.connect(backup_file) as source_db:
        with sqlite3.connect(restored_file) as target_db:
            source_db.backup(target_db)

    with sqlite3.connect(restored_file) as db:
        integrity = db.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        tables = db.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()

    if integrity is None or integrity[0] != "ok":
        raise RuntimeError("Restored database is corrupted")

    if not tables:
        raise RuntimeError("Restored database contains no tables")

    print(f"Restored from: {backup_file}")
    print(f"Restored database: {restored_file}")
    print(f"Tables restored: {len(tables)}")
    print("Integrity check: OK")


if __name__ == "__main__":
    main()
