---
phase: 1
slug: foundation
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-09
audited: 2026-03-09
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (latest) |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | SETUP-01 | unit | `pytest tests/test_db_manager.py::test_create_game -x` | ✅ | ✅ green |
| 1-01-02 | 01 | 0 | SETUP-02 | unit | `pytest tests/test_db_manager.py::test_create_game_defaults -x` | ✅ | ✅ green |
| 1-01-03 | 01 | 0 | SETUP-03 | unit | `pytest tests/test_db_manager.py::test_create_game_starting_airport -x` | ✅ | ✅ green |
| 1-01-04 | 01 | 0 | SETUP-04 | unit | `pytest tests/test_db_manager.py::test_get_latest_game -x` | ✅ | ✅ green |
| 1-01-05 | 01 | 1 | DB-01 | integration | `pytest tests/test_migrations.py::test_schema_after_migration -x` | ✅ | ✅ green |
| 1-01-06 | 01 | 1 | DB-02 | integration | `pytest tests/test_db_manager.py::test_persistence_roundtrip -x` | ✅ | ✅ green |
| 1-01-07 | 01 | 1 | DB-04 | smoke | `pytest tests/test_security.py::test_no_hardcoded_credentials -x` | ✅ | ✅ green |
| 1-01-08 | 01 | 1 | ARCH-02 | smoke | `pytest tests/test_architecture.py::test_sql_only_in_db_manager -x` | ✅ | ✅ green |
| 1-01-09 | 01 | 1 | ARCH-04 | smoke | `pytest tests/test_architecture.py::test_module_structure -x` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/__init__.py` — empty, marks tests as package
- [x] `tests/conftest.py` — shared fixtures (test DB connection, teardown)
- [x] `tests/test_db_manager.py` — stubs for SETUP-01, SETUP-02, SETUP-03, SETUP-04, DB-02
- [x] `tests/test_migrations.py` — stub for DB-01
- [x] `tests/test_security.py` — stub for DB-04 (grep-based, no DB needed)
- [x] `tests/test_architecture.py` — stubs for ARCH-02, ARCH-04 (import + grep-based, no DB needed)
- [x] `pip install pytest` — pytest 9.0.2 installed
- [x] `pip install mysql-connector-python` — 9.6.0 installed, confirmed on Python 3.14

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `python main.py` connects and presents menu | SETUP-01 / DB-01 | Requires live MariaDB at mysql.metropolia.fi | Run `python main.py`, confirm no connection error, confirm menu appears |
| `.env` file not committed | DB-04 | Git history check | Run `git log --all -- .env` and confirm no output; confirm `.gitignore` contains `.env` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s (9 tests in 0.25s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-03-09 — all 9/9 tests pass

---

## Validation Audit 2026-03-09

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Tests passing | 9/9 |
| Runtime | 0.25s |
