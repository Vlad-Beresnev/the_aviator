---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
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
| 1-01-01 | 01 | 0 | SETUP-01 | unit | `pytest tests/test_db_manager.py::test_create_game -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 0 | SETUP-02 | unit | `pytest tests/test_db_manager.py::test_create_game_defaults -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 0 | SETUP-03 | unit | `pytest tests/test_db_manager.py::test_create_game_starting_airport -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 0 | SETUP-04 | unit | `pytest tests/test_db_manager.py::test_get_latest_game -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01 | 1 | DB-01 | integration | `pytest tests/test_migrations.py::test_schema_after_migration -x` | ❌ W0 | ⬜ pending |
| 1-01-06 | 01 | 1 | DB-02 | integration | `pytest tests/test_db_manager.py::test_persistence_roundtrip -x` | ❌ W0 | ⬜ pending |
| 1-01-07 | 01 | 1 | DB-04 | smoke | `pytest tests/test_security.py::test_no_hardcoded_credentials -x` | ❌ W0 | ⬜ pending |
| 1-01-08 | 01 | 1 | ARCH-02 | smoke | `pytest tests/test_architecture.py::test_sql_only_in_db_manager -x` | ❌ W0 | ⬜ pending |
| 1-01-09 | 01 | 1 | ARCH-04 | smoke | `pytest tests/test_architecture.py::test_module_structure -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — empty, marks tests as package
- [ ] `tests/conftest.py` — shared fixtures (test DB connection, teardown)
- [ ] `tests/test_db_manager.py` — stubs for SETUP-01, SETUP-02, SETUP-03, SETUP-04, DB-02
- [ ] `tests/test_migrations.py` — stub for DB-01
- [ ] `tests/test_security.py` — stub for DB-04 (grep-based, no DB needed)
- [ ] `tests/test_architecture.py` — stubs for ARCH-02, ARCH-04 (import + grep-based, no DB needed)
- [ ] `pip install pytest` — pytest not detected in project
- [ ] `pip install mysql-connector-python` — not yet installed; verify Python 3.14 compat

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `python main.py` connects and presents menu | SETUP-01 / DB-01 | Requires live MariaDB at mysql.metropolia.fi | Run `python main.py`, confirm no connection error, confirm menu appears |
| `.env` file not committed | DB-04 | Git history check | Run `git log --all -- .env` and confirm no output; confirm `.gitignore` contains `.env` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
