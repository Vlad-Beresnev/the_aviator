---
phase: 01-foundation
plan: 01
subsystem: testing
tags: [pytest, mysql-connector-python, gitignore, test-scaffold, security, architecture]

# Dependency graph
requires: []
provides:
  - ".gitignore excluding .env, __pycache__, *.pyc from version control"
  - ".env.example template with all five DB_* placeholder vars"
  - "tests/ directory with full test scaffold (9 test items across 4 test files)"
  - "pytest 9.0.2 and mysql-connector-python 9.6.0 installed"
  - "conftest.py with db_connection fixture that skips gracefully without .env"
affects: [01-02-config-and-db-manager, 01-03-services-and-game-logic]

# Tech tracking
tech-stack:
  added: [pytest 9.0.2, mysql-connector-python 9.6.0]
  patterns: [test-scaffold-before-implementation, db-fixture-skip-without-env, sql-boundary-enforcement]

key-files:
  created:
    - .gitignore
    - .env.example
    - tests/__init__.py
    - tests/conftest.py
    - tests/test_db_manager.py
    - tests/test_migrations.py
    - tests/test_security.py
    - tests/test_architecture.py
  modified: []

key-decisions:
  - "mysql-connector-python used (not PyMySQL) — assignment constraint, confirmed working on Python 3.14"
  - "test_module_structure intentionally fails until plans 02-03 create the six required .py files"
  - "db_connection fixture uses pytest.skip (not fail) when .env is absent — allows CI without credentials"

patterns-established:
  - "Fixture skip pattern: session-scoped db_connection skips entire suite when no .env present"
  - "Exclusion pattern: db/populatedb.py excluded from security scan (run-once manual script)"
  - "SQL boundary test: glob *.py at project root, exclude db_manager.py, assert no SQL keywords"

requirements-completed: [DB-04, ARCH-02, ARCH-04]

# Metrics
duration: 2min
completed: 2026-03-09
---

# Phase 1 Plan 01: Test Scaffold and Safety Net Summary

**pytest scaffold with 9 test items, mysql-connector-python 9.6.0 on Python 3.14, .gitignore protecting .env, and architecture/security tests that run immediately without DB access**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-09T17:54:14Z
- **Completed:** 2026-03-09T17:55:50Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments

- .gitignore committed before any .env could be created — credentials never enter git history
- .env.example with all five DB_* vars checked in as safe template for onboarding
- 9-item test scaffold covering SETUP-01/02/03/04, DB-01, DB-02, DB-04, ARCH-02, ARCH-04
- test_security.py and test_sql_only_in_db_manager both pass immediately without any source modules
- conftest.py skips DB-touching tests gracefully when .env is absent

## Task Commits

Each task was committed atomically:

1. **Task 1: Project safety files — .gitignore and .env.example** - `cc69a13` (chore)
2. **Task 2: Install dependencies and create test scaffold** - `6403209` (feat)

## Files Created/Modified

- `.gitignore` - Excludes .env, __pycache__/, *.pyc, *.pyo, .pytest_cache/
- `.env.example` - Template with DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME placeholder values
- `tests/__init__.py` - Empty; marks tests/ as Python package
- `tests/conftest.py` - Session-scoped db_connection fixture; cleanup_test_game teardown fixture
- `tests/test_db_manager.py` - 5 stubs: create_game, defaults, starting airport, get_latest_game, persistence roundtrip
- `tests/test_migrations.py` - 1 stub: schema column verification via INFORMATION_SCHEMA
- `tests/test_security.py` - Grep-based; passes immediately; excludes db/populatedb.py
- `tests/test_architecture.py` - SQL boundary test passes immediately; module-existence test fails until plans 02-03

## Decisions Made

- mysql-connector-python 9.6.0 chosen over PyMySQL — assignment constraint. Confirmed it imports successfully on Python 3.14.0.
- test_module_structure is intentionally failing at this stage — the six required .py files (config, db_manager, airport_service, player_service, game_logic, main) do not exist yet. They are created in plans 02 and 03.
- db_connection fixture uses pytest.skip rather than pytest.fail — allows the test suite to run in CI environments or before credentials are available.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. mysql-connector-python 9.6.0 imports cleanly on Python 3.14.0. All 9 test items discovered.

## User Setup Required

**Before DB-touching tests can run**, create a `.env` file from `.env.example`:

```bash
cp .env.example .env
# Edit .env with your Metropolia credentials
```

Required env vars:
- `DB_HOST` — mysql.metropolia.fi
- `DB_PORT` — 3306
- `DB_USER` — Your Metropolia username
- `DB_PASSWORD` — Your Metropolia database password
- `DB_NAME` — Same as DB_USER (Metropolia convention)

## Next Phase Readiness

- Safety net in place — credentials can never be accidentally committed
- Test scaffold ready — plan 02 (config.py + db_manager.py) and plan 03 (services + game_logic + main.py) will turn the failing stubs green
- Architecture boundary tests already enforcing SQL-only-in-db_manager from first commit

---
*Phase: 01-foundation*
*Completed: 2026-03-09*

## Self-Check: PASSED

- All 8 files exist on disk
- Both task commits verified: cc69a13, 6403209
