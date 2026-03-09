---
phase: quick-2
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/conftest.py
  - tests/test_security.py
autonomous: true
requirements: [DB-01, DB-02, DB-04, SETUP-01, SETUP-02, SETUP-03, SETUP-04]

must_haves:
  truths:
    - "All 5 test_db_manager.py tests pass"
    - "test_schema_after_migration passes"
    - "test_no_hardcoded_credentials passes"
  artifacts:
    - path: "tests/conftest.py"
      provides: "db_connection fixture that runs migrations before tests use DB"
    - path: "tests/test_security.py"
      provides: "credential scan that excludes venv/ directory"
  key_links:
    - from: "tests/conftest.py db_connection fixture"
      to: "db_manager.run_migrations()"
      via: "direct call after connection established"
    - from: "tests/test_security.py glob pattern"
      to: "venv exclusion"
      via: "filter paths starting with venv/"
---

<objective>
Fix three categories of failing tests without changing production logic.

Purpose: Tests are failing due to missing migration call in the test fixture and an overly broad file glob that sweeps up pip vendored packages. Both are test infrastructure bugs, not application bugs.
Output: All failing tests pass; no production code changed.
</objective>

<execution_context>
@/Users/vlad/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
Root cause analysis:

1. game table missing (5 tests in test_db_manager.py, test_schema_after_migration):
   The `db_connection` fixture in tests/conftest.py opens a raw connection but never calls
   `db_manager.run_migrations()`. The `game` table is created only by that migration, so
   all tests that touch `game` fail with Table 'aviator_dev.game' doesn't exist.
   Fix: call `db_manager.run_migrations()` inside the `db_connection` fixture after the
   connection is established, before `yield conn`.

2. hardcoded credentials false positive (test_no_hardcoded_credentials):
   tests/test_security.py uses `glob.glob("**/*.py", recursive=True)` which includes
   venv/ — pip's vendored packages contain lines like `password=password` which trip the
   check. The fix is to skip any path that starts with "venv" (or ".venv") after normpath.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Run migrations in db_connection fixture</name>
  <files>/Users/vlad/dev/the_aviator/tests/conftest.py</files>
  <action>
    In the `db_connection` fixture, after the `conn = mysql.connector.connect(...)` call
    and before `yield conn`, add:

    ```python
    import db_manager
    db_manager.run_migrations()
    ```

    This ensures the `game` table and `airport.is_unlocked` column exist before any test
    that depends on `db_connection` runs. `run_migrations()` is already idempotent
    (uses CREATE TABLE IF NOT EXISTS and ALTER TABLE IF NOT EXISTS), so re-running it is safe.

    Do NOT change the `cleanup_test_game` fixture or any other part of the file.
  </action>
  <verify>
    <automated>cd /Users/vlad/dev/the_aviator && python3 -m pytest tests/test_db_manager.py tests/test_migrations.py -v 2>&1 | tail -20</automated>
  </verify>
  <done>All 5 test_db_manager.py tests and test_schema_after_migration pass (or skip if no .env).</done>
</task>

<task type="auto">
  <name>Task 2: Exclude venv from credential scan</name>
  <files>/Users/vlad/dev/the_aviator/tests/test_security.py</files>
  <action>
    In `test_no_hardcoded_credentials`, after building `py_files` with glob, add a filter
    to skip paths inside `venv/` or `.venv/`:

    Replace the existing `excluded = {...}` block and the `for path in py_files:` loop
    header so that venv paths are skipped. The simplest approach: add to the existing
    norm-check inside the loop:

    ```python
    # Skip virtual environment directories
    if norm.startswith("venv" + os.sep) or norm.startswith(".venv" + os.sep):
        continue
    ```

    Add this `continue` immediately after the existing excluded-set check (before opening
    the file). Do not change any other logic in the test.
  </action>
  <verify>
    <automated>cd /Users/vlad/dev/the_aviator && python3 -m pytest tests/test_security.py -v 2>&1 | tail -10</automated>
  </verify>
  <done>test_no_hardcoded_credentials passes with no violations reported.</done>
</task>

</tasks>

<verification>
Run all previously-failing tests together:

```
cd /Users/vlad/dev/the_aviator && python3 -m pytest tests/test_db_manager.py tests/test_migrations.py tests/test_security.py -v
```

Expected: all tests pass (or skip with "No .env file found" if credentials not configured — skips are acceptable, failures are not).
</verification>

<success_criteria>
- `tests/test_db_manager.py` — 5/5 pass (or 5/5 skip)
- `tests/test_migrations.py::test_schema_after_migration` — pass (or skip)
- `tests/test_security.py::test_no_hardcoded_credentials` — pass
- No production files (config.py, db_manager.py, main.py) modified
</success_criteria>

<output>
No SUMMARY.md needed for quick fixes. If desired, note completion in STATE.md under resolved issues.
</output>
