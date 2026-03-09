import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_schema_after_migration(db_connection):
    """DB-01: After migrations, game table has required columns; airport has is_unlocked."""
    cursor = db_connection.cursor()
    # Check game table columns
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'game'"
    )
    game_cols = {row[0] for row in cursor.fetchall()}
    for col in ("id", "name", "money", "battery_used", "global_awareness", "current_airport"):
        assert col in game_cols, f"game table missing column: {col}"
    # Check airport.is_unlocked
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'airport' AND COLUMN_NAME = 'is_unlocked'"
    )
    assert cursor.fetchone() is not None, "airport table missing is_unlocked column"
    cursor.close()
