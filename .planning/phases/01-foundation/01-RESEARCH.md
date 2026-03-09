# Phase 1: Foundation - Research

**Researched:** 2026-03-09
**Domain:** Python + mysql-connector-python + python-dotenv + MariaDB schema migrations
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Starting airport is fixed: SFO — San Francisco International (ident: KSFO, iata_code: SFO) — always the same for every new game
- Store the starting airport ident as a constant in `config.py`
- "Continue existing game" asks the player for their name, then loads the most recent row in the `game` table with that player name (ORDER BY id DESC LIMIT 1)
- If no record is found for the entered name: show a clear error message ("No game found for [name]") and re-prompt — do NOT auto-create a new game on continue
- New game and continue game are separate explicit flows from the startup menu
- Filter to `type='large_airport'` only when selecting a starting airport (~500 large airports globally)
- `mysql-connector-python` is the required DB library (assignment constraint)
- Controller-Service-Repository pattern is mandatory from the first commit — db_manager.py handles all SQL, services return plain dicts only
- Credentials must come from `.env` file — never hardcoded in source

### Claude's Discretion
- Migration safety: ALTER TABLE statements should be idempotent where possible (check if column exists before adding) — dev workflow should not crash on re-run
- `db/populatedb.py` credentials: leave as-is for now (run-once manual script) — not updated to .env in Phase 1
- Exact module skeleton depth: stub functions with docstrings and pass/return {} placeholders are sufficient — no logic in Phase 1 stubs

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SETUP-01 | Player can start a new game by entering their name | `INSERT INTO game` with player name; `db_manager.create_game()` covers this |
| SETUP-02 | New game initialized in DB with default values (money=5000, battery=1000, global_awareness=0) | Column defaults in CREATE TABLE + explicit INSERT values |
| SETUP-03 | Player is placed at a random starting airport on new game | Fixed KSFO constant in config.py; INSERT sets current_airport='KSFO' |
| SETUP-04 | Player can continue an existing game session (load latest game record) | `SELECT ... WHERE name=? ORDER BY id DESC LIMIT 1` in db_manager |
| DB-01 | Schema migrations applied: game table has money, global_awareness, battery_used columns; airport table has is_unlocked column | CREATE TABLE game (all columns) + ALTER TABLE airport ADD is_unlocked |
| DB-02 | All game state persists in MariaDB — no in-memory-only state | All writes go through db_manager; verified by re-loading state after restart |
| DB-04 | Database credentials loaded from .env file — never hardcoded in source code | python-dotenv load_dotenv() + os.getenv() in config.py |
| ARCH-02 | All SQL is contained in db_manager.py — no SQL strings in service or logic layers | Module skeleton stubs enforce boundary; linter-visible if violated |
| ARCH-04 | Module structure matches assignment: config.py, db_manager.py, airport_service.py, player_service.py, game_logic.py, main.py | Six files created as stubs with correct import chain |
</phase_requirements>

---

## Summary

Phase 1 is a pure infrastructure phase: create the database schema, wire credentials safely, and lay down the module skeleton that all subsequent phases build on. There is no game logic to implement — only the plumbing that makes game logic possible.

The existing `lp_project_base.sql` contains only `airport` and `country` tables. The `game` table does not exist in the database yet and must be created from scratch with all required columns (`id`, `name`, `money`, `battery_used`, `global_awareness`, `current_airport`, `is_unlocked`). The `airport` table already exists and only needs one new column (`is_unlocked BOOLEAN DEFAULT 0`).

The technology stack is minimal and constrained by the assignment: `mysql-connector-python` for all DB access, `python-dotenv` for credential loading, no ORM. The key architectural discipline is that `db_manager.py` is the only file that may contain SQL strings — all other modules call `db_manager` functions. This boundary must be enforced from the very first commit, not retrofitted later.

**Primary recommendation:** Create the `game` table fresh (do not attempt ALTER from a non-existent table), add `is_unlocked` to `airport` idempotently, implement `db_manager.py` with connection function + four stub-ready query functions, populate `config.py` with constants and `.env`-driven credentials, then create empty stub modules for the remaining four files.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| mysql-connector-python | latest (2.x / 9.x) | MariaDB/MySQL connection, cursor, execute | Assignment constraint; pure-Python, no C extension required |
| python-dotenv | 1.2.1 (already installed) | Load `.env` file into `os.environ` | Standard pattern for credential isolation; already present on this machine |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| os (stdlib) | stdlib | `os.getenv()` to read env vars loaded by dotenv | Always — after `load_dotenv()`, read via `os.getenv()` |
| pytest | latest | Test framework for validation architecture | Wave 0 gap — not installed yet |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| mysql-connector-python | PyMySQL, aiomysql | Assignment mandates mysql-connector-python; no choice |
| python-dotenv | configparser, raw os.environ | dotenv is standard for 12-factor apps; already installed |
| Raw CREATE TABLE | SQLAlchemy migrations | No ORM in this project; raw SQL is the right fit |

**Installation:**
```bash
pip install mysql-connector-python
# python-dotenv already installed at 1.2.1
# pytest for testing:
pip install pytest
```

---

## Architecture Patterns

### Recommended Project Structure

```
the_aviator/
├── .env                  # credentials (gitignored)
├── .gitignore            # must include .env
├── config.py             # DB constants + game constants (STARTING_AIRPORT, MAX_BATTERY)
├── db_manager.py         # ALL SQL lives here — connection + query functions
├── airport_service.py    # stub: future airport queries, no SQL
├── player_service.py     # stub: future player state updates, no SQL
├── game_logic.py         # stub: future game engine, no SQL
├── main.py               # stub: future CLI entry point, no SQL
└── db/
    ├── lp_project_base.sql    # existing airport/country data (already populated)
    └── populatedb.py          # existing run-once populate script (unchanged)
```

### Pattern 1: Credential Loading (config.py)

**What:** Load DB credentials from `.env` at module import time, expose as constants.
**When to use:** Every file that needs DB host/user/password imports from `config.py` only.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from working directory

DB_HOST = os.getenv("DB_HOST", "mysql.metropolia.fi")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Game constants
STARTING_AIRPORT = "KSFO"
MAX_BATTERY = 1000
STARTING_MONEY = 5000
```

### Pattern 2: Connection Function in db_manager.py

**What:** Single function that returns a fresh connection using config constants. No connection pooling needed at this scale.
**When to use:** Called at the start of every db_manager function; close connection in the same function.

```python
# db_manager.py
import mysql.connector
import config

def _get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )
```

### Pattern 3: Query Function Shape

**What:** Each public function in `db_manager.py` opens a connection, executes SQL, commits if write, closes, returns plain dict or list.
**When to use:** All DB operations.

```python
def create_game(player_name: str, airport_ident: str) -> dict:
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
    return {"id": game_id, "name": player_name, "money": config.STARTING_MONEY,
            "battery_used": 0, "global_awareness": 0, "current_airport": airport_ident}
```

### Pattern 4: Idempotent Column Addition

**What:** Before running `ALTER TABLE airport ADD COLUMN is_unlocked`, check if the column already exists using `INFORMATION_SCHEMA`.
**When to use:** Dev workflow — migration script must not crash on repeated runs.

```python
def _column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table, column)
    )
    return cursor.fetchone()[0] > 0

def run_migrations():
    conn = _get_connection()
    cursor = conn.cursor()

    # Create game table if not exists — fully idempotent
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

    # Idempotent: add is_unlocked to airport only if missing
    if not _column_exists(cursor, "airport", "is_unlocked"):
        cursor.execute(
            "ALTER TABLE airport ADD COLUMN is_unlocked BOOLEAN DEFAULT 0"
        )

    conn.commit()
    cursor.close()
    conn.close()
```

### Pattern 5: Load Game by Player Name

**What:** Retrieve the most recent game row for a given name.
**When to use:** "Continue game" flow.

```python
def get_latest_game(player_name: str) -> dict | None:
    conn = _get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM game WHERE name = %s ORDER BY id DESC LIMIT 1",
        (player_name,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row  # None if not found
```

### Pattern 6: Stub Module Shape

**What:** All non-db_manager modules are empty stubs with function signatures, docstrings, and `pass` or `return {}`.
**When to use:** All modules except `config.py` and `db_manager.py` in Phase 1.

```python
# airport_service.py
import db_manager

def get_reachable_airports(current_airport_ident: str, battery_remaining: float) -> list:
    """Return list of airports reachable from current location within battery range."""
    pass

def get_airport(ident: str) -> dict:
    """Return airport record as dict, or None if not found."""
    pass
```

### Anti-Patterns to Avoid

- **SQL in service files:** Any `SELECT`, `INSERT`, `UPDATE`, `DELETE` string outside `db_manager.py` violates ARCH-02 from day one. Search for `SELECT` in non-db_manager files as a verification step.
- **Hardcoded credentials:** `password="..."` in any `.py` file. The git history check in success criteria means this must never appear even in an early commit.
- **Global connection object:** Opening one connection at module level and reusing it. MariaDB connections time out; open/close per function is safer for this scale.
- **`cursor()` without `dictionary=True` when returning dicts:** Without `dictionary=True`, `fetchone()` returns a tuple — manual index access is fragile and unreadable.
- **`ALTER TABLE` without existence check:** Running `ALTER TABLE airport ADD COLUMN is_unlocked` on a table that already has the column raises a MySQL error. Use `IF NOT EXISTS` (MariaDB 10.0+) or the INFORMATION_SCHEMA check.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| .env file parsing | Custom file reader, configparser | `python-dotenv` `load_dotenv()` | Handles quoting, comments, multiline, already installed |
| DB column existence check | Custom SQL parser | `INFORMATION_SCHEMA.COLUMNS` query or `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` | MariaDB built-in; one line |
| Password masking in source | Custom obfuscation | `.env` + `.gitignore` | Git history is permanent; .env never enters repo |

**Key insight:** This phase has almost no logic to hand-roll. The risk is in discipline (SQL leaking into wrong files, credentials in source) not in algorithmic complexity.

---

## Common Pitfalls

### Pitfall 1: game Table Does Not Exist Yet

**What goes wrong:** Developer assumes the remote MariaDB already has a `game` table (because `high-level-plan.md` mentions ALTER TABLE) and runs ALTER statements on a non-existent table — crash.
**Why it happens:** `lp_project_base.sql` has only `airport` and `country`. The `game` table is never created in the base schema.
**How to avoid:** Phase 1 migration script uses `CREATE TABLE IF NOT EXISTS game (...)` with all columns defined from scratch. No ALTER TABLE on `game`.
**Warning signs:** `Table 'game' doesn't exist` error on first run.

### Pitfall 2: ALTER TABLE airport ADD COLUMN on Re-Run

**What goes wrong:** `ALTER TABLE airport ADD COLUMN is_unlocked BOOLEAN DEFAULT 0` succeeds first run, crashes on second run with "Duplicate column name 'is_unlocked'".
**Why it happens:** Standard ALTER TABLE is not idempotent.
**How to avoid:** Use `ALTER TABLE airport ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT 0` (MariaDB 10.0+ syntax) or check INFORMATION_SCHEMA first.
**Warning signs:** Error on second run of `python main.py` or migration script.

### Pitfall 3: Credentials in Git History

**What goes wrong:** Developer commits `config.py` with real password before adding `.env` pattern, even temporarily.
**Why it happens:** "I'll fix it in the next commit" — but git history is permanent without force-push rewrite.
**How to avoid:** `.gitignore` includes `.env` before the first commit. `config.py` uses `os.getenv()` only. Never write password string literals.
**Warning signs:** `git log -p` shows `password=` with actual value.

### Pitfall 4: Import Chain Is Wrong

**What goes wrong:** `game_logic.py` imports `db_manager` directly, or `main.py` imports `db_manager` directly, bypassing the service layer.
**Why it happens:** Convenience during stubbing.
**How to avoid:** Enforce the chain: `main.py` → `game_logic.py` → services → `db_manager`. Only `db_manager` imports `config`. Services import `db_manager` only.
**Warning signs:** `import db_manager` appearing in `main.py` or `game_logic.py`.

### Pitfall 5: cursor() Without dictionary=True

**What goes wrong:** `fetchone()` returns a tuple `(1, 'Alice', 5000, ...)` instead of `{'id': 1, 'name': 'Alice', 'money': 5000, ...}`. Services must return plain dicts (ARCH-01).
**Why it happens:** Default mysql-connector-python cursor returns tuples.
**How to avoid:** Use `cursor = conn.cursor(dictionary=True)` in all read functions in `db_manager.py`.
**Warning signs:** Service functions manually indexing into tuples like `row[2]`.

### Pitfall 6: Missing .env File at Runtime

**What goes wrong:** `load_dotenv()` silently does nothing if `.env` doesn't exist. `os.getenv("DB_PASSWORD")` returns `None`. Connection attempt fails with cryptic error.
**Why it happens:** New developer clones repo, no `.env.example` template provided.
**How to avoid:** Add a startup check in `db_manager.py` or `config.py` that asserts required env vars are not None, with a helpful error message pointing to `.env`.
**Warning signs:** `mysql.connector.errors.ProgrammingError: Failed to connect` with `None` in connection args.

---

## Code Examples

### .env File Format

```bash
# .env  (gitignored — never committed)
DB_HOST=mysql.metropolia.fi
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_username
```

### .gitignore Minimum

```
.env
__pycache__/
*.pyc
```

### Full game Table CREATE Statement

```sql
CREATE TABLE IF NOT EXISTS game (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    money INT DEFAULT 5000,
    battery_used DOUBLE DEFAULT 0,
    global_awareness INT DEFAULT 0,
    current_airport VARCHAR(40),
    FOREIGN KEY (current_airport) REFERENCES airport(ident)
);
```

### Idempotent airport Column Addition (MariaDB syntax)

```sql
ALTER TABLE airport ADD COLUMN IF NOT EXISTS is_unlocked BOOLEAN DEFAULT 0;
```

### Import Chain (correct)

```
main.py
  imports: game_logic
game_logic.py
  imports: airport_service, player_service, config
airport_service.py
  imports: db_manager
player_service.py
  imports: db_manager
db_manager.py
  imports: config, mysql.connector
config.py
  imports: os, dotenv
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded credentials in source | `.env` + `python-dotenv` | ~2015, 12-factor app era | Security; passwords never in git history |
| Connection pooling for small apps | Open/close per query | N/A for this scale | Simplicity wins; pooling adds complexity for a single-user CLI game |
| `ALTER TABLE` raw | `CREATE TABLE IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS` | MariaDB 10.0+ | Idempotent migrations; dev workflow never crashes on re-run |

**Deprecated/outdated:**
- `MySQLdb` / `MySQL-python`: Requires C extension, Python 2 era. Use `mysql-connector-python` instead (assignment mandates it).
- `co2_consumed` column: Replaced by `battery_used` per project narrative — do not create this column.

---

## Open Questions

1. **Remote MariaDB schema current state**
   - What we know: `lp_project_base.sql` was run once via `populatedb.py`, populating `airport` and `country`. No `game` table in base SQL.
   - What's unclear: Whether the remote DB at `mysql.metropolia.fi` already has any `game` table from previous experiments, or has `is_unlocked` on `airport` from manual work.
   - Recommendation: Use `CREATE TABLE IF NOT EXISTS` for `game` and `ADD COLUMN IF NOT EXISTS` for `is_unlocked` — both are safe regardless of current state. First task in Wave 0 should be a manual check or rely on idempotent migrations.

2. **mysql-connector-python version compatibility with Python 3.14**
   - What we know: Python 3.14.0 is installed. `mysql-connector-python` is not yet installed.
   - What's unclear: Whether the latest release of `mysql-connector-python` is compatible with Python 3.14 (released ~2024-2025, very new).
   - Recommendation: Run `pip install mysql-connector-python` during Wave 0 setup and verify import succeeds. If not, `PyMySQL` is a drop-in alternative (but assignment specifies `mysql-connector-python`).

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (latest) |
| Config file | none — Wave 0 gap |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SETUP-01 | `create_game("Alice", "KSFO")` returns dict with name="Alice" | unit | `pytest tests/test_db_manager.py::test_create_game -x` | Wave 0 |
| SETUP-02 | New game row has money=5000, battery_used=0, global_awareness=0 | unit | `pytest tests/test_db_manager.py::test_create_game_defaults -x` | Wave 0 |
| SETUP-03 | New game row has current_airport=KSFO (config.STARTING_AIRPORT) | unit | `pytest tests/test_db_manager.py::test_create_game_starting_airport -x` | Wave 0 |
| SETUP-04 | `get_latest_game("Alice")` returns most recent row; returns None for unknown name | unit | `pytest tests/test_db_manager.py::test_get_latest_game -x` | Wave 0 |
| DB-01 | After migrations, game table has required columns; airport has is_unlocked | integration | `pytest tests/test_migrations.py::test_schema_after_migration -x` | Wave 0 |
| DB-02 | Value inserted via create_game() is readable via get_latest_game() | integration | `pytest tests/test_db_manager.py::test_persistence_roundtrip -x` | Wave 0 |
| DB-04 | No password string literal in any .py file (checked via grep) | smoke | `pytest tests/test_security.py::test_no_hardcoded_credentials -x` | Wave 0 |
| ARCH-02 | No SQL string (SELECT/INSERT/UPDATE/DELETE) outside db_manager.py | smoke | `pytest tests/test_architecture.py::test_sql_only_in_db_manager -x` | Wave 0 |
| ARCH-04 | All six required .py files exist and import without error | smoke | `pytest tests/test_architecture.py::test_module_structure -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/__init__.py` — empty, marks tests as package
- [ ] `tests/conftest.py` — shared fixtures (test DB connection, teardown)
- [ ] `tests/test_db_manager.py` — covers SETUP-01, SETUP-02, SETUP-03, SETUP-04, DB-02
- [ ] `tests/test_migrations.py` — covers DB-01
- [ ] `tests/test_security.py` — covers DB-04 (grep-based, no DB needed)
- [ ] `tests/test_architecture.py` — covers ARCH-02, ARCH-04 (import + grep-based, no DB needed)
- [ ] Framework install: `pip install pytest` — pytest not detected in project

**Note on DB tests:** Tests that actually write to the remote MariaDB at `mysql.metropolia.fi` require valid credentials in `.env`. Architecture and security tests (ARCH-02, ARCH-04, DB-04) are grep/import-based and run without DB access — these are the safe smoke tests for CI.

---

## Sources

### Primary (HIGH confidence)

- Direct inspection of `/Users/vlad/dev/the_aviator/db/lp_project_base.sql` — confirmed only `airport` and `country` tables exist (no `game` table)
- Direct inspection of `/Users/vlad/dev/the_aviator/db/populatedb.py` — confirmed mysql-connector-python connection pattern, host/port
- Direct inspection of `01-CONTEXT.md` — locked decisions, existing code patterns
- `python-dotenv` 1.2.1 confirmed installed via pip show
- Python 3.14.0 confirmed via `python3 --version`

### Secondary (MEDIUM confidence)

- MariaDB `ADD COLUMN IF NOT EXISTS` syntax — standard MariaDB 10.0+ feature; well-documented
- mysql-connector-python `dictionary=True` cursor parameter — standard documented feature

### Tertiary (LOW confidence)

- mysql-connector-python compatibility with Python 3.14 — not verified; package not installed; Python 3.14 is very recent. Needs validation in Wave 0.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — mysql-connector-python is assignment-mandated; python-dotenv confirmed installed
- Architecture: HIGH — module structure, import chain, and SQL boundary rules are all explicitly specified in CONTEXT.md and REQUIREMENTS.md
- Pitfalls: HIGH — game table absence confirmed by direct SQL inspection; credential pattern confirmed by existing populatedb.py
- Python 3.14 + mysql-connector-python compatibility: LOW — needs Wave 0 verification

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable libraries; 30-day window)
