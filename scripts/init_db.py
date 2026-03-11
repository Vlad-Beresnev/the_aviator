#!/usr/bin/env python3
"""Initialize the database for The Aviator.

Loads the airport data from db/lp_project_base.sql and runs game migrations.
Reads credentials from .env (see .env.example).

Usage:
    python scripts/init_db.py
"""

import os
import sys

# Allow importing project modules when run from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import db_manager


def main():
    sql_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "db", "lp_project_base.sql",
    )

    if not os.path.exists(sql_path):
        print(f"ERROR: SQL file not found at {sql_path}")
        sys.exit(1)

    print(f"Connecting to {config.DB_HOST}:{config.DB_PORT} as {config.DB_USER} ...")

    # 1. Load airport data
    print(f"Loading airport data from {sql_path} ...")
    with open(sql_path, "r") as f:
        sql_script = f.read()

    conn = db_manager._get_connection()
    cursor = conn.cursor()
    try:
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
        print("Airport data loaded.")
    except Exception as e:
        conn.rollback()
        print(f"ERROR loading airport data: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

    # 2. Run game table migrations
    print("Running migrations ...")
    db_manager.run_migrations()
    print("Migrations complete.")

    print("\nDatabase ready! Run the game with: python main.py")


if __name__ == "__main__":
    main()
