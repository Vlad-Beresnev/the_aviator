---
phase: 01-foundation
plan: 02
subsystem: database
tags: [mysql-connector-python, dotenv, config, db-manager, migrations, tdd]

# Dependency graph
requires:
  - phase: 01-foundation plan 01
    provides: "pytest scaffold, conftest.py with db_connection fixture, test_security.py, test_architecture.py"
provides:
  - "config.py exposing 8 module-level constants (DB_HOST/PORT/USER/PASSWORD/NAME + STARTING_AIRPORT/MAX_BATTERY/STARTING_MONEY) loaded from .env"
  - "db_manager.py with _get_connection, _column_exists, run_migrations, create_game, get_latest_game"
  - "run_migrations() idempotent — creates game table and adds is_unlocked to airport"
  - "create_game(name, ident) returns plain dict with id/name/money/battery_used/global_awareness/current_airport"
  - "get_latest_game(name) returns dict or None via dictionary=True cursor"
affects: [01-03-services-and-game-logic, 01-04-main]

# Tech tracking
tech-stack:
  added: [python-dotenv]
  patterns: [fail-fast-credentials, open-close-per-function-no-pooling, dictionary-cursor, idempotent-migrations]

key-files:
  created:
    - config.py
    - db_manager.py
  modified: []

key-decisions:
  - "Fail-fast EnvironmentError on import if DB credentials missing — surfaces config issues before cryptic mysql failures"
  - "Open/close connection per function — no pooling — matches assignment scope and avoids connection state bugs"
  - "dictionary=True cursor in get_latest_game — returns dict directly, no manual column mapping"
  - "game table FOREIGN KEY on current_airport references airport(ident) — enforces referential integrity from first row"

patterns-established:
  - "Config import pattern: import config at top of db_manager.py, access config.DB_* for all connection params"
  - "Migration idempotency: CREATE TABLE IF NOT EXISTS + ALTER TABLE ADD COLUMN IF NOT EXISTS (MariaDB syntax)"
  - "Return plain dicts from all CRUD functions — JSON-serializable, no ORM objects"

requirements-completed: [SETUP-01, SETUP-02, SETUP-03, SETUP-04, DB-01, DB-02, DB-04, ARCH-02]

# Metrics
duration: 3min
completed: 2026-03-09
---

# Phase 1 Plan 02: Config and DB Manager Summary

**config.py with dotenv credential loading and game constants, plus db_manager.py containing all SQL: idempotent migrations, create_game returning plain dict, get_latest_game returning dict or None**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-09T17:57:59Z
- **Completed:** 2026-03-09T18:01:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- config.py with fail-fast EnvironmentError replaces cryptic mysql connection failures when .env is missing
- db_manager.py contains 100% of the SQL for Phase 1 — architecture boundary tests enforce this from day one
- run_migrations() idempotent: game table created, is_unlocked column added to airport — safe to call on every startup
- create_game/get_latest_game contract matches test scaffold from plan 01 exactly

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement config.py and verify with architecture test** - `2eec9cc` (feat)
2. **Task 2: Implement db_manager.py — migrations and CRUD** - `8c1719d` (feat)

## Files Created/Modified

- `config.py` - Loads DB credentials from .env, exposes 8 constants, fails fast if credentials absent
- `db_manager.py` - All SQL for Phase 1: _get_connection, _column_exists, run_migrations, create_game, get_latest_game

## Decisions Made

- Fail-fast EnvironmentError on import when DB_USER/DB_PASSWORD/DB_NAME missing — better UX than cryptic mysql failures downstream
- Open/close connection per function (no pooling) — appropriate for assignment scope, avoids connection lifecycle bugs
- dictionary=True on cursor in get_latest_game — returns column-name-keyed dict directly, no tuple unpacking
- game table FOREIGN KEY referencing airport(ident) — enforces DB-level referential integrity

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. test_module_structure failure (missing airport_service.py, player_service.py, game_logic.py, main.py) is expected and documented in plan 01 SUMMARY — these are created in plan 03.

## User Setup Required

**Before DB-touching tests can run**, create a `.env` file from `.env.example`:

```bash
cp .env.example .env
# Edit .env with your Metropolia credentials
```

Required env vars: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

With valid .env, run: `pytest tests/test_migrations.py tests/test_db_manager.py -v`

## Next Phase Readiness

- config.py and db_manager.py are stable — plan 03 can import them immediately
- All SQL is in db_manager.py — architecture tests enforce this boundary going forward
- DB tests skip gracefully without .env — CI-friendly

---
*Phase: 01-foundation*
*Completed: 2026-03-09*

## Self-Check: PASSED

- config.py exists at /Users/vlad/dev/the_aviator/config.py
- db_manager.py exists at /Users/vlad/dev/the_aviator/db_manager.py
- SUMMARY.md exists at /Users/vlad/dev/the_aviator/.planning/phases/01-foundation/01-02-SUMMARY.md
- Task commits verified: 2eec9cc, 8c1719d
