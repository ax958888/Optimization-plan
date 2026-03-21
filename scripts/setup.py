#!/usr/bin/env python3
"""
Alkaid Self-Optimization System v2 — Setup Script
Initializes learning directories and database on CPX31.
"""
import os
import sqlite3
from pathlib import Path


def setup():
    learning_dir = Path("/root/.kiro/learning")
    daily_dir = learning_dir / "daily"
    db_path = learning_dir / "insights.db"
    schema_path = Path(__file__).parent.parent / "schema" / "insights.sql"

    # Create directories
    daily_dir.mkdir(parents=True, exist_ok=True)
    print("Created: %s" % daily_dir)

    # Ensure .learnings/ exists
    learnings_dir = Path("/root/.kiro/.learnings")
    learnings_dir.mkdir(parents=True, exist_ok=True)
    print("Verified: %s" % learnings_dir)

    # Initialize database
    if db_path.exists():
        print("Database already exists: %s" % db_path)
        # Run schema anyway (IF NOT EXISTS is safe)
    else:
        print("Creating database: %s" % db_path)

    if schema_path.exists():
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        conn = sqlite3.connect(str(db_path))
        conn.executescript(schema_sql)
        conn.close()
        print("Schema applied successfully")
    else:
        print("WARNING: Schema file not found at %s" % schema_path)
        print("Run from the project root directory")

    # Verify
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    print("\nSetup complete!")
    print("Database: %s" % db_path)
    print("Tables: %s" % ", ".join(tables))
    print("Daily dir: %s" % daily_dir)
    print("\nNext steps:")
    print("1. Integrate collector into kanban-kiro-bot (see scheduler.py)")
    print("2. Add digest handler to alkaid-bot")
    print("3. Restart both services")


if __name__ == "__main__":
    setup()
