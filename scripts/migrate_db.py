#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Database Migration
Applies schema updates to existing insights.db.
"""
import sqlite3
from pathlib import Path


def migrate():
    db_path = Path("/root/.kiro/learning/insights.db")
    schema_path = Path(__file__).parent.parent / "schema" / "insights.sql"

    if not db_path.exists():
        print("Database not found. Run setup.py first.")
        return

    if not schema_path.exists():
        print("Schema file not found at %s" % schema_path)
        return

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(str(db_path))

    # Get existing tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = set(row[0] for row in cursor.fetchall())
    print("Existing tables: %s" % ", ".join(sorted(existing)))

    # Apply schema (IF NOT EXISTS makes this safe)
    conn.executescript(schema_sql)

    # Check new tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    updated = set(row[0] for row in cursor.fetchall())
    new_tables = updated - existing

    conn.close()

    if new_tables:
        print("New tables created: %s" % ", ".join(sorted(new_tables)))
    else:
        print("No new tables needed (schema is up to date)")

    print("Migration complete.")


if __name__ == "__main__":
    migrate()
