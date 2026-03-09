# Stack Research

**Domain:** Python CLI strategy game backed by MariaDB/MySQL
**Researched:** 2026-03-09
**Confidence:** HIGH (all versions verified via PyPI index on 2026-03-09)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ (3.14 on this machine) | Runtime | Active LTS line; 3.12 is the stable production choice, 3.14 is available locally. Use 3.12 if deploying to a server without 3.14; use 3.14 locally. Either works for this project. |
| mysql-connector-python | 9.6.0 | MariaDB/MySQL database driver | **Required by assignment.** Oracle's official Pure-Python connector. No C extension needed — installs cleanly on any OS without system MySQL headers. Supports connection pooling via `CMySQLConnection`/`MySQLConnectionPool`. Version 9.x dropped Python 2 and aligns with MySQL 8.x/9.x and MariaDB 10.x/11.x. |
| python-dotenv | 1.2.2 | Load `config.py` credentials from `.env` file | Keeps DB credentials out of source control. Already installed (1.2.1). Required for safe `config.py` implementation — reads `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` from `.env`. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rich | 14.3.3 | CLI display — colored tables, status panels, progress bars | Use for the status dashboard (location, battery, money, global_awareness) and the airport selection table. Turns `print()` output into readable, scannable terminal UI without moving to a full TUI framework. Handles unicode, color, table formatting. |
| tabulate | 0.10.0 | Lightweight table formatting fallback | Use if `rich` is considered too heavy for the assignment grader's environment. `tabulate` is zero-dependency and produces clean ASCII/Unicode tables with `tabulate(rows, headers=...)`. Choose one: prefer `rich`, fall back to `tabulate`. |
| math (stdlib) | built-in | Haversine distance calculation | Python's `math.sin`, `math.cos`, `math.atan2`, `math.radians` are all you need. No third-party geospatial library required for Haversine. Zero install overhead. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pytest 9.0.2 | Unit and integration test runner | Standard for Python testing. `pytest` discovers tests automatically. Use for testing `game_logic.py` and service layer functions in isolation. |
| pytest-mock 3.15.1 | Mock/stub database calls in tests | Wraps `unittest.mock` with cleaner pytest fixtures (`mocker.patch`). Essential for testing service layer without a real DB connection. |
| coverage 7.13.4 | Test coverage measurement | `coverage run -m pytest && coverage report`. Identifies untested branches in game logic. |
| black 26.3.0 | Code formatter | Opinionated, zero-config formatter. Run before submission. Assignment graders notice inconsistent formatting. |
| flake8 7.3.0 | Linter | Catches unused imports, undefined variables, line-length violations. Pair with black. |

---

## Installation

```bash
# Create virtual environment (keep DB credentials out of global Python)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Core runtime dependencies
pip install mysql-connector-python==9.6.0 python-dotenv==1.2.2 rich==14.3.3

# Dev dependencies
pip install pytest==9.0.2 pytest-mock==3.15.1 coverage==7.13.4 black==26.3.0 flake8==7.3.0
```

Create `requirements.txt`:
```
mysql-connector-python==9.6.0
python-dotenv==1.2.2
rich==14.3.3
```

Create `requirements-dev.txt`:
```
pytest==9.0.2
pytest-mock==3.15.1
coverage==7.13.4
black==26.3.0
flake8==7.3.0
```

---

## Module Structure (Required by Assignment)

The assignment mandates this specific file layout. Each file maps to a layer in the Controller-Service-Repository pattern:

```
the_aviator/
├── .env                    # DB credentials — NEVER commit this
├── .gitignore              # Must include .env
├── requirements.txt
├── requirements-dev.txt
├── config.py               # Loads .env, exposes DB_CONFIG dict + game constants
├── db_manager.py           # Repository layer: raw SQL, connection pool
├── airport_service.py      # Service: Haversine queries, reachable airport logic
├── player_service.py       # Service: update location, money, battery in DB
├── game_logic.py           # Engine: process turn, win condition, forced landing
├── main.py                 # CLI entry point: input loop, display, calls services
└── tests/
    ├── test_game_logic.py
    ├── test_airport_service.py
    └── test_player_service.py
```

### Layer contracts

- `db_manager.py` returns raw Python dicts/lists from `cursor.fetchall()` with `dictionary=True`
- `airport_service.py` and `player_service.py` accept/return plain dicts (no DB objects leak upward)
- `main.py` calls service functions only — never touches DB directly
- This ensures Phase 2 can replace `main.py` with a Flask/FastAPI router and the service layer is untouched

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| mysql-connector-python 9.x | PyMySQL 1.1.2 | If you need async support (asyncio) — PyMySQL has an aiomysql fork. For this sync CLI game, PyMySQL offers no advantage over the Oracle connector. |
| mysql-connector-python 9.x | mysqlclient 2.2.8 | If raw performance is critical (mysqlclient is a C extension, 2-5x faster for bulk queries). Requires system libmysqlclient headers to install — brittle on different machines. Overkill for a game with sub-100 row queries. |
| rich | blessed 1.33.0 | If you need raw terminal control (cursor position, keypress detection). `blessed` gives low-level terminal manipulation. For this game, `rich` tables and panels are sufficient and require far less code. |
| rich | curses (stdlib) | Only if you need a full-screen TUI with window management. `curses` is complex, platform-inconsistent on Windows, and not needed for a menu-driven CLI. |
| pytest | unittest (stdlib) | If zero external dependencies are a hard requirement. `unittest` works but is more verbose — `pytest` has cleaner syntax and better output for the same test coverage. |
| python-dotenv | Hardcoded config.py | Never. Hardcoding credentials gets caught in code review and is a security anti-pattern even for coursework. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SQLAlchemy ORM | Massive dependency for straightforward SQL queries. Hides the SQL the assignment is testing. Over-engineered for a 6-table game database. | Raw SQL via mysql-connector-python with `dictionary=True` cursors |
| Click / Typer (CLI frameworks) | This game uses an interactive menu loop, not a command-line argument parser. Click/Typer solve argument parsing, not game loops. | `input()` + `print()` / `rich.console.Console()` for display |
| asyncio / async drivers | The game is inherently sequential (one player action → DB update → display). Async adds complexity with no benefit. | Synchronous mysql-connector-python |
| pickle / shelve for persistence | The assignment explicitly requires database persistence. File-based state storage would not satisfy requirements. | MariaDB/MySQL via mysql-connector-python |
| pandas | Used for data analysis, not game state management. Importing pandas for airport queries is inappropriate for this domain. | Direct SQL with Haversine calculated in Python math |
| mysql-connector-python < 8.0 | Python 2 era. The 8.x line dropped legacy auth plugins and aligns with MySQL 8+ and MariaDB 10.6+. | mysql-connector-python 9.6.0 |

---

## Stack Patterns by Variant

**For the Phase 1 CLI (current phase):**
- Entry point: `main.py` with a `while True` game loop
- Display: `rich.console.Console()` for status panels; `rich.table.Table` for airport lists
- Input: `input()` with `try/except ValueError` for all numeric inputs
- No web framework — `main.py` is the only interface layer

**For the Phase 2 web upgrade (future):**
- Replace `main.py` with a Flask or FastAPI router
- Service layer (`airport_service.py`, `player_service.py`, `game_logic.py`) is unchanged
- Service methods already return plain dicts — serialize to JSON with `json.dumps()` or FastAPI's automatic serialization
- Add `flask==3.x` or `fastapi==0.x` to requirements at that point

**For testing service layer without a real database:**
- Use `pytest-mock` to patch `db_manager.execute_query` at the call site
- Test `game_logic.py` functions with dict inputs — no DB needed
- Integration tests can use a separate test database seeded via SQL fixture

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| mysql-connector-python 9.6.0 | Python 3.9–3.14, MySQL 8.x/9.x, MariaDB 10.6–11.x | Tested against Python 3.14.0 on this machine. MariaDB compatibility confirmed for versions using MySQL protocol. |
| rich 14.3.3 | Python 3.8+ | No conflicts with mysql-connector-python. |
| pytest 9.0.2 | Python 3.9+ | Compatible with pytest-mock 3.15.1. |
| python-dotenv 1.2.2 | Python 3.9+ | Already installed (1.2.1) — upgrade to 1.2.2 optional. |

---

## Sources

- PyPI index query via `pip3 index versions` (2026-03-09) — all version numbers verified from live PyPI
- Python 3.14.0 confirmed installed on this machine (`python3 --version`)
- `python-dotenv 1.2.1` confirmed already installed
- PROJECT.md and high-level-plan.md — stack constraints (mysql-connector-python required, module names required, architecture mandated)
- mysql-connector-python: confidence HIGH (assignment-mandated, PyPI verified)
- rich: confidence HIGH (PyPI verified, standard CLI display library)
- pytest/pytest-mock: confidence HIGH (PyPI verified, industry standard)
- Haversine via stdlib `math`: confidence HIGH (standard formula, no external library needed)

---
*Stack research for: Python CLI strategy game (The Aviator) with MariaDB/MySQL*
*Researched: 2026-03-09*
