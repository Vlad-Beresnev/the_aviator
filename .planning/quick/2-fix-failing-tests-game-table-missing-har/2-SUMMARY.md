---
phase: quick-2
plan: 01
subsystem: tests
tags: [test-infra, db, security]
dependency_graph:
  requires: []
  provides: [working-test-fixtures]
  affects: [tests/conftest.py, tests/test_security.py]
tech_stack:
  added: []
  patterns: [idempotent-migration-call-in-fixture, venv-exclusion-filter]
key_files:
  created: []
  modified:
    - tests/conftest.py
    - tests/test_security.py
decisions:
  - "Call db_manager.run_migrations() inside db_connection fixture — migrations are idempotent so safe to call on every test session start"
  - "Filter venv/ and .venv/ by prefix after normpath — simpler and more robust than glob exclusion patterns"
metrics:
  duration: "~3 minutes"
  completed: "2026-03-09"
  tasks: 2
  files: 2
---

# Quick Task 2: Fix Failing Tests (game table missing, hardcoded credentials false positive) Summary

**One-liner:** Fixed test infra by calling run_migrations() in db_connection fixture and filtering venv/ from credential scan glob.

## What Was Done

Two test infrastructure bugs fixed without touching any production code.

### Task 1: Run migrations in db_connection fixture

**File:** `tests/conftest.py`
**Commit:** da66e7a

Added `db_manager.run_migrations()` call inside the `db_connection` fixture, immediately after the MySQL connection is established and before `yield conn`. The `game` table and `airport.is_unlocked` column are created only by migrations — without this call, any test touching the `game` table would fail with "Table 'aviator_dev.game' doesn't exist".

The call is safe to add unconditionally because `run_migrations()` uses `CREATE TABLE IF NOT EXISTS` / `ALTER TABLE ... IF NOT EXISTS`, making it fully idempotent.

### Task 2: Exclude venv from credential scan

**File:** `tests/test_security.py`
**Commit:** e36267f

Added a `continue` guard immediately after the excluded-set check in `test_no_hardcoded_credentials` to skip any path whose normpath starts with `venv/` or `.venv/`. The existing `glob.glob("**/*.py", recursive=True)` pattern was sweeping up pip vendored packages (e.g., `urllib3`, `requests`) which contain lines like `password=password` that trip the check legitimately but are not project code.

## Verification Results

```
tests/test_db_manager.py::test_create_game            SKIPPED (no .env)
tests/test_db_manager.py::test_create_game_defaults   SKIPPED (no .env)
tests/test_db_manager.py::test_create_game_starting_airport SKIPPED (no .env)
tests/test_db_manager.py::test_get_latest_game        SKIPPED (no .env)
tests/test_db_manager.py::test_persistence_roundtrip  SKIPPED (no .env)
tests/test_migrations.py::test_schema_after_migration SKIPPED (no .env)
tests/test_security.py::test_no_hardcoded_credentials PASSED

1 passed, 6 skipped
```

Skips are acceptable per success criteria — no .env credentials present in CI environment.

## Deviations from Plan

None - plan executed exactly as written.

## Self-Check: PASSED

- tests/conftest.py modified: FOUND
- tests/test_security.py modified: FOUND
- Commit da66e7a: FOUND
- Commit e36267f: FOUND
- No production files modified: CONFIRMED
