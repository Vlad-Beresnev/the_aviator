# Project Research Summary

**Project:** The Aviator
**Domain:** Python CLI educational strategy game with MariaDB/MySQL persistence, designed for CLI-to-web upgrade
**Researched:** 2026-03-09
**Confidence:** HIGH (stack verified from PyPI; architecture mandated by assignment; pitfalls drawn from documented failure modes)

## Executive Summary

The Aviator is a single-player Python CLI strategy game where a player pilots around the world delivering sustainability lectures, managing battery and money resources, and unlocking airports across continents. The game is explicitly designed as Phase 1 of a two-phase academic project — Phase 2 upgrades the same codebase to a web application. This architectural constraint is the dominant force shaping every design decision: the Controller-Service-Repository pattern is mandatory, services must return plain dicts (never mutable objects), and no print/display logic may exist outside `main.py`. The stack is minimal and assignment-constrained: `mysql-connector-python` is required, `python-dotenv` handles credential safety, and `rich` provides readable terminal output.

The recommended build order follows the dependency graph dictated by the architecture: establish the database connection and schema first, then implement the repository layer (`db_manager.py`), then the service layer (`airport_service.py`, `player_service.py`), then the controller (`game_logic.py`), and finally wire the CLI (`main.py`). Every feature in the game — flying, lecturing, recharging, forced landing, win condition — depends on this foundation being correct. The core gameplay loop is straightforward; the complexity is almost entirely in maintaining clean layer boundaries and handling edge cases (battery empty mid-flight, new game vs. load game, multi-step transactional state updates).

The top risk is not technical difficulty — the game logic itself is simple. The risk is architectural drift: SQL leaking into service methods, print statements buried in game logic, mutable objects returned from services, or transaction boundaries left open. All of these are invisible during Phase 1 testing but become expensive blockers when Phase 2 web upgrade begins. Prevention requires enforcing layer contracts as non-negotiable rules from the first commit, not as a cleanup task at the end.

---

## Key Findings

### Recommended Stack

The stack is tightly constrained by the assignment. `mysql-connector-python 9.6.0` is required — it is the Oracle official Pure-Python connector, installs without system headers, and supports MariaDB 10.6–11.x. `python-dotenv 1.2.2` is required for safe `config.py` implementation (DB credentials must not be committed to git). `rich 14.3.3` is the recommended display library for colored status panels and airport tables; `tabulate 0.10.0` is a fallback if the grader environment restricts dependencies. All geospatial calculation uses Python's stdlib `math` module — no third-party library is needed for Haversine.

Python 3.12+ is the target runtime (3.14 is available locally). No ORM (SQLAlchemy is explicitly excluded as over-engineered and counter-educational for this project). No async drivers (the game is inherently sequential). No CLI frameworks (Click/Typer solve argument parsing, not game loops). State persistence is exclusively in MariaDB — no file-based state, no in-memory singletons.

**Core technologies:**
- `mysql-connector-python 9.6.0`: database driver — required by assignment, Pure-Python, no C extension needed
- `python-dotenv 1.2.2`: credential management — keeps DB password out of source control and git history
- `rich 14.3.3`: CLI display — colored tables and status panels with zero complex terminal code
- `math` (stdlib): Haversine distance — pure Python, no geospatial library overhead

**Dev tools:**
- `pytest 9.0.2` + `pytest-mock 3.15.1`: testing with database call mocking
- `coverage 7.13.4`: test coverage measurement
- `black 26.3.0` + `flake8 7.3.0`: formatting and linting before submission

### Expected Features

The game's feature set is fully defined by the assignment. Every P1 feature is low-complexity but all are required — none are optional. The dependency chain is strict: Haversine calculator must exist before airport listing; airport listing must work before flying; flying must work before lecturing; lecturing feeds the win condition. Feature research identified several anti-features that should be explicitly rejected: CO2 tracking (contradicts the core action), real-time flight animation (brittle, adds no gameplay value), ASCII map rendering (fragile across terminal widths), and random weather events (undermines strategic planning).

**Must have (Phase 1 table stakes):**
- New game setup with player name and random starting airport
- Haversine distance calculator (gates all navigation)
- List reachable airports with battery cost, speaker fee, difficulty
- Fly to chosen airport (battery deduction, location update, persist to DB)
- Lecture at current airport (global_awareness increment, money award, is_unlocked = 1)
- Recharge battery (money cost, battery restore, persist)
- Forced landing on battery empty (teleport to nearest airport, money penalty)
- Status display after every action (location, battery, money, global_awareness, airports unlocked)
- Win condition check after each action (continent spread or $1M threshold)
- Invalid input re-prompting (never crash on bad input)

**Should have (add once core loop is working):**
- Continue vs new game prompt on startup
- Narrative flavor text (forced landing messages, win screen story beat)

**Defer (v2+ only):**
- Web interface (Phase 2 — service layer already designed for this)
- Difficulty scaling affecting fee payout formula
- Multiple win paths with different narrative endings

**Explicit anti-features (do not build):**
- CO2 tracking as player metric
- Real-time / animated flight sequences
- Leaderboard / high scores
- Random weather or mechanical failure events
- Multiple aircraft or upgrade trees

### Architecture Approach

The architecture is mandated by the assignment and follows the Controller-Service-Repository pattern across five required files: `config.py` (credentials and constants), `db_manager.py` (all SQL, repository boundary), `airport_service.py` (Haversine, reachability logic), `player_service.py` (game state CRUD), `game_logic.py` (rule enforcement, action orchestration), and `main.py` (CLI loop, display only). The dependency direction is strictly one-way: `main.py` calls only `game_logic.py`; the controller calls services; services call only `db_manager.py`; the repository calls MariaDB. No upward dependencies, no circular imports, no SQL outside `db_manager.py`, no print calls outside `main.py`.

The key design contract enabling Phase 2: every service returns plain Python dicts. `mysql-connector-python`'s `dictionary=True` cursor means rows are already dicts at the repository boundary — no mapping step required. Phase 2 wraps the same `game_logic.py` calls in Flask route handlers and calls `jsonify()` instead of `print()`. The service and controller layers are untouched.

**Major components:**
1. `config.py` — DB credentials from `.env`, game constants (battery max, recharge rate); read by all layers
2. `db_manager.py` — all raw SQL execution, connection management, returns `list[dict]`; the sole file that touches MariaDB
3. `airport_service.py` — Haversine pure function, bounding-box pre-filter query, reachability list; no game state awareness
4. `player_service.py` — game state CRUD, battery/money mutations, lecture delivery, win stat queries
5. `game_logic.py` — orchestrates services for each user action, enforces game rules, checks win conditions, returns result dicts
6. `main.py` — CLI game loop, parses input, calls `game_logic`, renders result dicts as terminal output

### Critical Pitfalls

Nine critical pitfalls were identified. These five are the highest-impact and most likely to occur:

1. **Connection leak per repository call** — calling `mysql.connector.connect()` inside each repository method exhausts MariaDB's `max_connections` during extended play. Prevent by initializing one shared connection or `MySQLConnectionPool(pool_size=2)` in `db_manager.py` at startup; never call `connect()` inside a query method.

2. **Business logic embedded in the repository layer** — putting Haversine calculations or battery-range filtering inside `db_manager.py` or as SQL stored procedures collapses the service boundary and makes Phase 2 impossible. Repository returns raw airport rows; service applies all game rules.

3. **Services returning mutable objects instead of plain dicts** — returning a `Player` class instance from `player_service.get_game()` makes Phase 2 JSON serialization impossible and enables in-place mutation anti-patterns. All service return types must be `dict` or `list[dict]`.

4. **No transaction wrapping on multi-step state updates** — a flight action updates battery, money, and airport unlock status. A crash between writes leaves inconsistent state. Wrap composite operations in explicit transactions with `try/except/rollback`.

5. **No separation between new game and load game** — always inserting a new `game` row on startup orphans existing progress; always loading the latest row makes test isolation impossible. Design explicit `create_new_game()` and `load_game(game_id)` entry points from the first commit.

Additional integration gotchas to address at the repository boundary:
- Use `%s` placeholders (not `?`) for parameterized queries in `mysql-connector-python`
- Cast `DECIMAL` lat/lon columns to `float()` — returned as Python `Decimal`, which breaks Haversine math
- Normalize `is_unlocked` boolean columns from `1/0` integers to `bool()` at the repository boundary
- Always call `connection.commit()` after writes — `autocommit` defaults to `False`

---

## Implications for Roadmap

The architecture's build order is not a stylistic preference — it is a hard dependency graph. Each layer cannot be correctly tested without the layer below it. The roadmap must follow this order.

### Phase 1: Project Foundation and Database Layer
**Rationale:** Everything else depends on a working database connection and correct schema. Credentials must be handled safely from the first commit — retroactive `.gitignore` additions do not remove committed secrets from git history.
**Delivers:** Working `config.py` with `.env` loading, `db_manager.py` with shared connection/pool, schema migrations applied to existing MariaDB instance, `.gitignore` with `.env` and no hardcoded credentials.
**Addresses:** New game vs. load game separation (must be designed here, not retrofitted); schema correctness (all required columns: `money`, `global_awareness`, `battery_used`, `is_unlocked` on `game` and `airport` tables).
**Avoids:** Connection leak pitfall, credential exposure pitfall, schema mismatch discovered late in development.
**Research flag:** Standard patterns — no additional research needed. `mysql-connector-python` pooling and `python-dotenv` usage are well-documented.

### Phase 2: Service Layer (Airport + Player)
**Rationale:** Services are the core of the application and the primary Phase 2 upgrade enabler. Layer contracts (plain dict returns, no print calls, no SQL strings) must be established and enforced before any game logic is written against them.
**Delivers:** `airport_service.py` with Haversine pure function and bounding-box-filtered reachable airport query; `player_service.py` with game state CRUD, battery/money mutations, and lecture delivery logic. All return types are `dict` or `list[dict]`.
**Uses:** `mysql-connector-python` `dictionary=True` cursor; stdlib `math` for Haversine; bounding-box WHERE clause with index on `(lat, lon)` for performance.
**Implements:** Service layer of CSR pattern; establishes the no-print, no-mutable-object contracts that protect Phase 2.
**Avoids:** Business logic in repository, mutable object returns, print calls in services, full airport table scan without bounding-box filter.
**Research flag:** Standard patterns — Haversine formula is well-documented; bounding-box SQL pre-filter is a standard geographic optimization. No additional research needed.

### Phase 3: Game Controller and Win Conditions
**Rationale:** `game_logic.py` can only be implemented correctly after both services exist and return correct data. Win condition logic requires both `airport_service` (continent spread) and `player_service` (money/global_awareness stats).
**Delivers:** `game_logic.py` with `create_game()`, `load_game()`, `fly_to_airport()`, `deliver_lecture()`, `recharge_battery()`, `check_win_condition()`. Forced landing logic (nearest airport teleport + penalty) implemented here. All actions wrapped in transactions via `db_manager`.
**Implements:** Controller layer; multi-step transactional state updates; win condition evaluation.
**Avoids:** Transaction-less multi-step updates; game logic bypassing the service layer; win condition check being skipped after certain actions.
**Research flag:** Standard patterns — game rule orchestration is well-defined in the architecture research. No external research needed.

### Phase 4: CLI Presentation Layer
**Rationale:** `main.py` is built last because it is purely I/O wiring over a complete controller. Building the CLI before the controller is complete invites coupling display logic into game rules.
**Delivers:** `main.py` with game loop, new/continue/quit startup menu, numbered airport selection, status display after every action, input validation with re-prompting (never crash on bad input), forced landing feedback, win screen with narrative text. `rich` tables for airport list; `rich` panels for status display.
**Uses:** `rich 14.3.3` for display; `python-dotenv` already loaded via `config.py`; calls `game_logic.py` functions exclusively.
**Avoids:** Print calls bleeding into service/controller layers; input validation logic in `game_logic.py`; hardcoded `game_id=1` shortcuts.
**Research flag:** Standard patterns — `rich` API is well-documented. No research needed.

### Phase 5: Testing and Polish
**Rationale:** Service layer functions are pure (Haversine, battery math) or easily mockable (`db_manager` calls). Tests are cheapest to write alongside the code but are scheduled last to avoid blocking the core loop delivery.
**Delivers:** `pytest` test suite for `game_logic.py`, `airport_service.py`, `player_service.py` with `pytest-mock` to stub DB calls. Coverage report. `black` formatting pass. `flake8` clean. `requirements.txt` and `requirements-dev.txt` finalized.
**Avoids:** Untested forced-landing edge case (empty result set on nearest-airport query); win condition silently skipped; battery recharge allowing negative money.
**Research flag:** Standard patterns — `pytest`/`pytest-mock` usage is well-documented. No research needed.

### Phase Ordering Rationale

- **Bottom-up dependency order:** DB layer → services → controller → CLI is the only order where each phase can be tested without mocking the phase above it. Building top-down produces untestable stubs and deferred integration debt.
- **Phase 2 (web upgrade) readiness is a cross-cutting constraint:** Every phase enforces the contracts that make Phase 2 possible — plain dict returns, no print in services, all SQL in `db_manager`. These are not cleanup tasks; they are build-time requirements.
- **Feature dependencies cluster naturally into phases:** All P1 features from FEATURES.md fit within Phases 1-4. There are no features that require out-of-order implementation.
- **Pitfall prevention is structural, not procedural:** The most dangerous pitfalls (connection leak, business logic in repository, mutable object returns) are prevented by the phase structure itself — not by reminders or code review after the fact.

### Research Flags

Phases with standard, well-documented patterns (no additional research-phase needed):
- **Phase 1:** `mysql-connector-python` pooling, `python-dotenv` — official documentation sufficient
- **Phase 2:** Haversine formula, bounding-box SQL filter — standard geographic patterns
- **Phase 3:** Game state orchestration, transaction wrapping — standard CSR pattern, well-defined by architecture research
- **Phase 4:** `rich` CLI display, input validation loop — well-documented library with clear API
- **Phase 5:** `pytest`/`pytest-mock` — industry-standard tooling with extensive documentation

No phases require a `/gsd:research-phase` deep-dive. All patterns are either assignment-mandated or drawn from well-established, high-confidence sources.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified from live PyPI index on 2026-03-09; `mysql-connector-python` is assignment-mandated; `python-dotenv 1.2.1` already installed |
| Features | MEDIUM | Based on project documents (HIGH confidence) + training knowledge of CLI game UX conventions (MEDIUM confidence); no live search available; well-established patterns unlikely to have changed |
| Architecture | HIGH | Architecture is assignment-mandated (PROJECT.md explicitly requires CSR pattern and file layout); patterns are standard and well-documented; no interpretation required |
| Pitfalls | HIGH | All pitfalls drawn from documented `mysql-connector-python` behavior, known CSR antipatterns, and reproducible failure modes; not speculative |

**Overall confidence:** HIGH

### Gaps to Address

- **Win condition specifics:** The exact continent-spread threshold (how many continents = win?) and the $1M money threshold are referenced but not definitively specified in the research. Validate against the assignment specification (`Määrittelydokumentin_pohja.md`) during Phase 3 implementation.
- **Schema state of the existing database:** The research notes required columns (`money`, `global_awareness`, `battery_used`, `is_unlocked`) but the current state of the MariaDB instance is not verified. Phase 1 must include a schema audit against the real database before writing any repository code.
- **Airport dataset size:** Research notes "realistic 3,000+ airports" as a bounding-box optimization threshold, but the actual dataset size for this project is unconfirmed. Verify during Phase 2 to determine if the bounding-box filter is required or if a full table scan is acceptable for the grader's dataset.

---

## Sources

### Primary (HIGH confidence)
- `.planning/PROJECT.md`, `high-level-plan.md`, `Määrittelydokumentin_pohja.md` — assignment requirements, file layout, architecture mandates, game rules
- PyPI index query via `pip3 index versions` (2026-03-09) — all package version numbers verified from live PyPI
- `mysql-connector-python` official documentation — connection pooling, cursor behavior, `%s` placeholder syntax, `DECIMAL` type mapping, `autocommit` default
- Python `math` stdlib documentation — Haversine implementation via `sin`, `cos`, `atan2`, `radians`

### Secondary (MEDIUM confidence)
- Training knowledge of Python CLI game conventions and text-adventure UX patterns (Zork, Inform 7, Finnish AMK coursework patterns) — feature expectations and anti-feature identification
- Educational game design principles (feedback loops, consequence vs. game-over, resource constraints as metaphor) — win condition and forced landing design rationale
- Controller-Service-Repository pattern documentation — layer boundary contracts, dependency direction rules
- Flask/FastAPI hexagonal architecture migration patterns — Phase 2 upgrade rationale and plain-dict contract

### Tertiary (LOW confidence)
- None. All findings in this summary are supported by primary or secondary sources.

---
*Research completed: 2026-03-09*
*Ready for roadmap: yes*
