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
    # ENGINE=InnoDB and CHARACTER SET latin1 on current_airport must match airport.ident
    # (airport table is latin1); mismatched charsets cause errno 150 on FK creation.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            money INT DEFAULT 5000,
            battery_used DOUBLE DEFAULT 0,
            global_awareness INT DEFAULT 0,
            current_airport VARCHAR(40) CHARACTER SET latin1,
            FOREIGN KEY (current_airport) REFERENCES airport(ident)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    """)

    # Add is_unlocked to airport table if missing (idempotent — MariaDB IF NOT EXISTS syntax)
    cursor.execute(
        "ALTER TABLE airport ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT 0"
    )

    # Create goal table: maps each large airport to a speaker_fee and difficulty_level
    # airport_ident is a FK to airport.ident (latin1 to match charset)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goal (
            id INT AUTO_INCREMENT PRIMARY KEY,
            airport_ident VARCHAR(40) CHARACTER SET latin1 NOT NULL UNIQUE,
            target_minvalue INT NOT NULL,
            target_maxvalue INT NOT NULL,
            FOREIGN KEY (airport_ident) REFERENCES airport(ident)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1
    """)

    # Populate goal table with all large airports if empty
    cursor.execute("SELECT COUNT(*) FROM goal")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "SELECT ident FROM airport WHERE type = 'large_airport'"
        )
        large_airports = cursor.fetchall()
        # Seed deterministic speaker_fee/difficulty from airport ident hash
        import hashlib
        rows = []
        for (ident,) in large_airports:
            h = int(hashlib.md5(ident.encode()).hexdigest(), 16)
            speaker_fee = 1000 + (h % 9001)   # $1,000 – $10,000
            difficulty = 1 + (h % 5)           # 1 – 5
            rows.append((ident, speaker_fee, difficulty))
        cursor.executemany(
            "INSERT IGNORE INTO goal (airport_ident, target_minvalue, target_maxvalue) VALUES (%s, %s, %s)",
            rows
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


def get_airport(ident: str) -> dict | None:
    """Return a single airport record as a dict, or None if ident not found."""
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT ident, name, municipality, latitude_deg, longitude_deg, continent, type, is_unlocked "
        "FROM airport WHERE ident = %s",
        (ident,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_large_airports() -> list:
    """Return all large_airport rows as a list of dicts (ident, name, municipality, lat, lon, continent, is_unlocked)."""
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT ident, name, municipality, latitude_deg, longitude_deg, continent, is_unlocked "
        "FROM airport WHERE type = 'large_airport'"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def update_game_state(game_id: int, current_airport: str, money: float, battery_used: float) -> None:
    """Update location, money, and battery_used for a game row by id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE game SET current_airport = %s, money = %s, battery_used = %s WHERE id = %s",
        (current_airport, money, battery_used, game_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_goal(airport_ident: str) -> dict | None:
    """
    Return the goal record for a large airport as a plain dict:
        {airport_ident, speaker_fee, difficulty}
    Returns None if no goal entry exists for this airport.
    """
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT airport_ident, target_minvalue AS speaker_fee, target_maxvalue AS difficulty "
        "FROM goal WHERE airport_ident = %s",
        (airport_ident,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_goals() -> dict:
    """
    Return all goal records as a dict keyed by airport_ident.
    Each value is a plain dict: {airport_ident, speaker_fee, difficulty}.
    Used to avoid N+1 queries in get_reachable_airports().
    """
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT airport_ident, target_minvalue AS speaker_fee, target_maxvalue AS difficulty FROM goal"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row["airport_ident"]: row for row in rows}


def is_airport_unlocked(airport_ident: str) -> bool:
    """Return True if the airport has is_unlocked = 1, False otherwise."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_unlocked FROM airport WHERE ident = %s",
        (airport_ident,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return bool(row and row[0])


def mark_airport_unlocked(airport_ident: str) -> None:
    """Set is_unlocked = 1 for the given airport ident."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE airport SET is_unlocked = 1 WHERE ident = %s",
        (airport_ident,)
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_game_after_lecture(game_id: int, new_money: float, new_global_awareness: int) -> None:
    """Update money and global_awareness after a successful lecture."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE game SET money = %s, global_awareness = %s WHERE id = %s",
        (new_money, new_global_awareness, game_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_unlocked_continents() -> list:
    """Return a list of distinct continent codes for airports with is_unlocked = 1."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT continent FROM airport WHERE is_unlocked = 1"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


def get_unlocked_count() -> int:
    """Return the number of airports with is_unlocked = 1."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM airport WHERE is_unlocked = 1")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def update_after_recharge(game_id: int, new_money: float, new_battery_used: float) -> None:
    """Update money and battery_used after a recharge action."""
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE game SET money = %s, battery_used = %s WHERE id = %s",
            (new_money, new_battery_used, game_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def fly_transaction(game_id: int, current_airport: str, money: float, battery_used: float) -> None:
    """Update location, money, and battery_used in a single explicit transaction."""
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE game SET current_airport = %s, money = %s, battery_used = %s WHERE id = %s",
            (current_airport, money, battery_used, game_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def deliver_lecture_transaction(game_id: int, airport_ident: str, new_money: float, new_global_awareness: int) -> None:
    """Mark airport unlocked and update money/awareness in a single transaction."""
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE airport SET is_unlocked = 1 WHERE ident = %s",
            (airport_ident,)
        )
        cursor.execute(
            "UPDATE game SET money = %s, global_awareness = %s WHERE id = %s",
            (new_money, new_global_awareness, game_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def delete_test_game(player_name: str) -> None:
    """Delete all game rows for a given player name. Used by smoke test cleanup."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM game WHERE name = %s", (player_name,))
    conn.commit()
    cursor.close()
    conn.close()


def mark_airport_locked(airport_ident: str) -> None:
    """Reset is_unlocked = 0 for the given airport. Used by smoke test cleanup."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE airport SET is_unlocked = 0 WHERE ident = %s",
        (airport_ident,)
    )
    conn.commit()
    cursor.close()
    conn.close()
