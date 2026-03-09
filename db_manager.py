import mysql.connector
import config


def _get_connection():
    """Return a fresh mysql-connector connection. Open/close per function — no pooling."""
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )


def _column_exists(cursor, table: str, column: str) -> bool:
    """Check if a column exists in a table using INFORMATION_SCHEMA."""
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column)
    )
    return cursor.fetchone()[0] > 0


def run_migrations():
    """Apply schema migrations. Idempotent — safe to call on every app startup."""
    conn = _get_connection()
    cursor = conn.cursor()

    # Create game table if not exists (game table does NOT exist in lp_project_base.sql)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            money INT DEFAULT 5000,
            battery_used DOUBLE DEFAULT 0,
            global_awareness INT DEFAULT 0,
            current_airport VARCHAR(40),
            FOREIGN KEY (current_airport) REFERENCES airport(ident)
        )
    """)

    # Add is_unlocked to airport table if missing (idempotent — MariaDB IF NOT EXISTS syntax)
    cursor.execute(
        "ALTER TABLE airport ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT 0"
    )

    conn.commit()
    cursor.close()
    conn.close()


def create_game(player_name: str, airport_ident: str) -> dict:
    """
    Insert a new game row with default values and return it as a plain dict.

    Args:
        player_name: Player's name (stored in 'name' column)
        airport_ident: Starting airport ident (e.g. 'KSFO')

    Returns:
        dict with keys: id, name, money, battery_used, global_awareness, current_airport
    """
    conn = _get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO game (name, money, battery_used, global_awareness, current_airport)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (player_name, config.STARTING_MONEY, 0, 0, airport_ident))
    conn.commit()
    game_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return {
        "id": game_id,
        "name": player_name,
        "money": config.STARTING_MONEY,
        "battery_used": 0,
        "global_awareness": 0,
        "current_airport": airport_ident,
    }


def get_latest_game(player_name: str) -> dict | None:
    """
    Return the most recent game row for a given player name, or None if not found.

    Uses ORDER BY id DESC LIMIT 1 — most recently inserted row wins.
    """
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)   # dictionary=True: returns dict not tuple
    cursor.execute(
        "SELECT * FROM game WHERE name = %s ORDER BY id DESC LIMIT 1",
        (player_name,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row  # None if player_name not found
