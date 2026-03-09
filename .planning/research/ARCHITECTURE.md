# Architecture Research

**Domain:** Python CLI game with MySQL/MariaDB backend, designed for CLI-to-web upgrade
**Researched:** 2026-03-09
**Confidence:** HIGH — project has mandated architecture; this documents the standard patterns and their rationale

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                          │
│                                                                  │
│  Phase 1: CLI (main.py)         Phase 2: Web (Flask routes)      │
│  ┌──────────────────────┐       ┌──────────────────────────┐    │
│  │  main.py             │       │  app.py / routes/*.py    │    │
│  │  - parse user input  │  →→→  │  - HTTP request parsing  │    │
│  │  - print output      │       │  - JSON serialization    │    │
│  │  - game loop         │       │  - route handlers        │    │
│  └──────────┬───────────┘       └────────────┬─────────────┘    │
├─────────────┼───────────────────────────────┼────────────────── ┤
│             │       CONTROLLER LAYER         │                   │
│             ▼                                ▼                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  game_logic.py                                           │   │
│  │  - orchestrates service calls for each user action       │   │
│  │  - enforces game rules (battery limits, win conditions)  │   │
│  │  - returns plain Python dicts (Phase 1) / dicts that     │   │
│  │    become JSON (Phase 2) — same data, different renderer │   │
│  └──────────────────────┬───────────────────────────────────┘   │
├─────────────────────────┼────────────────────────────────────── ┤
│                         │       SERVICE LAYER                    │
│          ┌──────────────┴──────────────┐                        │
│          ▼                             ▼                        │
│  ┌───────────────────┐      ┌─────────────────────┐            │
│  │  airport_service  │      │  player_service      │            │
│  │  - find airports  │      │  - manage game state │            │
│  │  - Haversine calc │      │  - battery/money ops │            │
│  │  - reachability   │      │  - lecture delivery  │            │
│  └────────┬──────────┘      └──────────┬───────────┘            │
├───────────┼─────────────────────────────┼──────────────────── ──┤
│           │       REPOSITORY LAYER      │                        │
│           ▼                             ▼                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  db_manager.py                                           │   │
│  │  - all raw SQL execution                                 │   │
│  │  - returns dicts/lists of dicts (never raw cursors)      │   │
│  │  - connection lifecycle management                       │   │
│  └──────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                       DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  MariaDB / MySQL                                         │   │
│  │  - airport (id, name, lat, lon, is_unlocked, country,    │   │
│  │             continent)                                   │   │
│  │  - game (id, player_name, money, battery_used,           │   │
│  │           global_awareness, current_airport_id)          │   │
│  │  - goal (id, airport_id, speaker_fee, difficulty_level)  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| `main.py` | Game loop, user input/output, render decisions | `game_logic.py` only |
| `game_logic.py` | Game rule enforcement, action orchestration, state transitions | `airport_service.py`, `player_service.py` |
| `airport_service.py` | Airport queries, Haversine distance, reachability filtering | `db_manager.py` only |
| `player_service.py` | Player/game state CRUD, battery/money mutations, lecture logic | `db_manager.py` only |
| `db_manager.py` | Raw SQL execution, connection pooling, result marshalling | MariaDB/MySQL only |
| `config.py` | DB credentials, game constants (battery max, recharge rate) | Read by `db_manager.py` and services |

## Recommended Project Structure

```
the_aviator/
├── config.py              # DB connection config, game constants
├── db_manager.py          # Repository layer — all SQL lives here
├── airport_service.py     # Service: airport queries + distance logic
├── player_service.py      # Service: player/game state management
├── game_logic.py          # Controller: rule enforcement + orchestration
├── main.py                # Presentation: CLI game loop
├── requirements.txt       # mysql-connector-python (and nothing else for Phase 1)
└── .planning/             # Project planning artifacts
```

### Phase 2 upgrade adds (without touching existing files):

```
the_aviator/
├── [all Phase 1 files unchanged]
├── app.py                 # Flask entry point
├── routes/
│   ├── game_routes.py     # POST /game, POST /fly, POST /lecture, etc.
│   └── airport_routes.py  # GET /airports, GET /airports/nearby
└── requirements.txt       # add Flask, flask-cors, gunicorn
```

### Structure Rationale

- **Flat module layout (no subdirectories in Phase 1):** Assignment constraint. Also appropriate for a project of this scope — layers are separated by file naming convention, not directory hierarchy.
- **`config.py` imported by everyone who needs it:** Single source of truth for constants. Avoids magic numbers scattered across services.
- **`db_manager.py` as the sole SQL file:** Enforces the repository boundary. Services never write SQL strings; they call `db_manager` functions. This is the key seam for testability and Phase 2 upgrade.
- **`game_logic.py` as controller (not `main.py`):** `main.py` handles only I/O. Game rules, win conditions, and action sequencing live in `game_logic.py`. When Phase 2 arrives, `game_logic.py` is called by Flask route handlers instead of `main.py` — no logic moves.

## Architectural Patterns

### Pattern 1: Controller-Service-Repository (CSR)

**What:** Three-layer separation of concerns. Controller orchestrates, Service encapsulates domain logic, Repository handles persistence.

**When to use:** Any project where the persistence technology or the presentation layer may change. Here: CLI → Web upgrade is the explicit driver.

**Trade-offs:** Small overhead for a CLI-only game. Worth it here because the assignment explicitly requires this pattern and Phase 2 reuse is the goal.

**Example:**

```python
# game_logic.py (Controller)
def fly_to_airport(game_id: int, target_airport_id: int) -> dict:
    game = player_service.get_game(game_id)
    origin = airport_service.get_airport(game["current_airport_id"])
    target = airport_service.get_airport(target_airport_id)
    distance = airport_service.haversine(origin, target)
    battery_cost = distance * 0.1
    if battery_cost > game["battery"]:
        return {"success": False, "reason": "insufficient_battery"}
    player_service.deduct_battery(game_id, battery_cost)
    player_service.move_to_airport(game_id, target_airport_id)
    return {"success": True, "battery_cost": battery_cost, "new_location": target}

# airport_service.py (Service)
def get_airports_in_range(origin_id: int, battery: float) -> list[dict]:
    origin = get_airport(origin_id)
    all_airports = db_manager.fetch_all_airports()
    return [
        {**a, "distance": haversine(origin, a), "battery_cost": haversine(origin, a) * 0.1}
        for a in all_airports
        if haversine(origin, a) * 0.1 <= battery and a["id"] != origin_id
    ]

# db_manager.py (Repository)
def fetch_all_airports() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, lat, lon, is_unlocked, continent FROM airport")
    return cursor.fetchall()
```

### Pattern 2: Return Plain Dicts (Never ORM Objects or Raw Cursors)

**What:** Every layer boundary returns Python dicts or lists of dicts. No custom classes, no ORM model instances, no raw `cursor` objects passed upward.

**When to use:** Always, in this project. Mandated by the CLI-to-web upgrade requirement.

**Trade-offs:** Slightly less type safety than dataclasses. Offset by using `dictionary=True` on the mysql-connector cursor, which means rows are already dicts — no mapping step needed.

**Why this enables Phase 2:** `json.dumps(dict)` works directly. Flask's `jsonify()` accepts dicts. The service layer output is already "pre-JSON." The only Phase 2 change is wrapping the controller call in `jsonify()` instead of printing it.

```python
# Phase 1 — main.py prints the dict
result = game_logic.fly_to_airport(game_id, target_id)
print(f"Flew to {result['new_location']['name']}, used {result['battery_cost']:.1f} battery")

# Phase 2 — Flask route returns the same dict as JSON
@app.route("/fly", methods=["POST"])
def fly():
    data = request.get_json()
    result = game_logic.fly_to_airport(data["game_id"], data["target_airport_id"])
    return jsonify(result)
```

### Pattern 3: Connection-per-Operation (Simple Connection Management)

**What:** Open a connection, execute query, close connection. No persistent connection or connection pool.

**When to use:** Single-player CLI game. At most one concurrent user. No need for pooling complexity.

**Trade-offs:** Slightly slower than a persistent connection (TCP handshake per call). Acceptable because:
1. MariaDB local connections are fast (<5ms)
2. Queries are infrequent (user-driven, not background polling)
3. Phase 2 (Flask) would upgrade to a connection pool via `mysql-connector-python`'s built-in pooling or SQLAlchemy

```python
# db_manager.py
import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
```

## Data Flow

### User Action Flow (Phase 1 — CLI)

```
User types input
    ↓
main.py          — parses input string, calls game_logic function
    ↓
game_logic.py    — validates action, calls service(s) to read state
    ↓
*_service.py     — calls db_manager to fetch needed data
    ↓
db_manager.py    — executes SELECT, returns list[dict]
    ↓
*_service.py     — applies domain logic (Haversine, battery math)
    ↓
game_logic.py    — enforces rules, calls service(s) to write state
    ↓
*_service.py     — calls db_manager to persist mutations
    ↓
db_manager.py    — executes INSERT/UPDATE
    ↑
game_logic.py    — returns result dict to main.py
    ↑
main.py          — renders result dict as terminal output
```

### User Action Flow (Phase 2 — Web, same middle layers)

```
HTTP POST /fly
    ↓
Flask route      — parses JSON body, calls game_logic function (SAME CALL)
    ↓
game_logic.py    — [identical to Phase 1]
    ↓
*_service.py     — [identical to Phase 1]
    ↓
db_manager.py    — [identical to Phase 1]
    ↑
Flask route      — wraps result dict in jsonify(), returns HTTP 200
```

### Key Data Flows

1. **New game creation:** `main.py` → `game_logic.create_game(name)` → `player_service.create_game()` → `db_manager.insert_game()` + `db_manager.get_random_airport()` → returns `{game_id, player_name, starting_airport, battery, money}`

2. **Fly action:** `main.py` → `game_logic.fly_to_airport(game_id, target_id)` → `airport_service.haversine()` (pure, no DB) + `player_service.deduct_battery()` + `player_service.move_to_airport()` → returns result dict

3. **Lecture delivery:** `main.py` → `game_logic.deliver_lecture(game_id)` → `player_service.get_game()` + `airport_service.get_goal()` + `player_service.add_money()` + `player_service.increment_awareness()` + `player_service.unlock_airport()` → returns result dict with win condition check

4. **Forced landing:** Triggered within `game_logic.fly_to_airport()` when battery would hit zero — `airport_service.find_nearest_airport()` → `player_service.teleport_to()` + `player_service.deduct_money(penalty)` → returns `{forced_landing: True, ...}`

5. **Win check:** Embedded in `game_logic` after every action — `player_service.get_game_stats()` → checks `global_awareness` threshold OR `money >= 1_000_000`

## Scaling Considerations

This is a single-player CLI game. Scaling in the traditional sense (concurrent users) is not applicable for Phase 1.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Phase 1: 1 user, CLI | Current design — connection-per-operation, no pooling needed |
| Phase 2: web, low concurrency | Add Flask + connection pool (`pool_size=5` in `mysql.connector.connect()`) |
| Phase 2: web, higher concurrency | Switch to SQLAlchemy with connection pooling, add gunicorn workers |

### Phase 2 First Bottleneck

The `get_airports_in_range()` function fetches all airports then filters in Python. At ~3,000 airports (realistic for a world airport database), this is fine. At 10,000+ airports, move the Haversine filter into a SQL bounding-box pre-filter (lat/lon range) before the precise calculation.

## Anti-Patterns

### Anti-Pattern 1: SQL in `main.py` or `game_logic.py`

**What people do:** Write `cursor.execute("SELECT * FROM airport WHERE ...")` directly in the game loop or controller.

**Why it's wrong:** Breaks the repository boundary. Phase 2 upgrade requires finding and moving all SQL strings. Testing game logic requires a real database. Schema changes require hunting across files.

**Do this instead:** All SQL lives exclusively in `db_manager.py`. Controllers and services call named functions like `db_manager.get_airports_near(lat, lon, radius)`.

### Anti-Pattern 2: Printing Inside Service or Controller

**What people do:** Call `print()` inside `game_logic.py` or `*_service.py` to show game status.

**Why it's wrong:** Services become untestable and un-reusable. Phase 2 would output garbage to the HTTP response stream. The CLI and web presentations can never diverge if display logic is buried in the domain layer.

**Do this instead:** Services and controllers return dicts. Only `main.py` (Phase 1) or Flask routes (Phase 2) call `print()` or `jsonify()`.

### Anti-Pattern 3: Game State in Python Variables (Not Database)

**What people do:** Store current battery, money, location as module-level variables or a singleton object in Python memory.

**Why it's wrong:** Game state is lost on exit. Phase 2 (stateless HTTP) cannot use in-process state at all — each request is a new Python context.

**Do this instead:** All mutable game state lives in the `game` database table. Every action reads state from DB, applies mutation, writes back. The game is stateless at the application layer.

### Anti-Pattern 4: Mixing Haversine Calculation Into the Repository

**What people do:** Put the Haversine formula inside `db_manager.py` or in a SQL stored procedure.

**Why it's wrong:** Haversine is pure domain logic with no I/O. Burying it in the repository layer makes it untestable without a database. Stored procedures create a Phase 2 migration headache.

**Do this instead:** Haversine lives in `airport_service.py` as a pure Python function. It takes two `(lat, lon)` pairs and returns kilometers. It never touches the DB.

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `main.py` → `game_logic.py` | Direct Python function calls | `main.py` is the only caller of `game_logic`; Phase 2 Flask routes replace `main.py` here |
| `game_logic.py` → `*_service.py` | Direct Python function calls | Controller can call both services; services do NOT call each other |
| `*_service.py` → `db_manager.py` | Direct Python function calls | Services import `db_manager`; `db_manager` has no knowledge of services |
| `db_manager.py` → MariaDB | `mysql-connector-python` | `dictionary=True` cursor ensures rows come back as dicts, not tuples |

### Dependency Direction (strictly enforced)

```
main.py
  → game_logic.py
      → airport_service.py → db_manager.py → MariaDB
      → player_service.py  → db_manager.py → MariaDB
config.py  ← imported by db_manager.py and optionally services
```

No upward dependencies. No circular imports. `db_manager.py` does not import from services. Services do not import from `game_logic.py`.

## Build Order Implications

The dependency graph dictates this build order:

1. **`config.py`** — no dependencies; needed by everything below
2. **`db_manager.py`** — depends only on `config.py`; must exist before any service can be tested
3. **Schema migrations** — `is_unlocked` column, `money`/`global_awareness` on `game` table; must match what services expect
4. **`airport_service.py`** — depends on `db_manager.py`; Haversine can be built and unit-tested before DB integration
5. **`player_service.py`** — depends on `db_manager.py`; CRUD for game state
6. **`game_logic.py`** — depends on both services; can only be integration-tested after services work
7. **`main.py`** — depends on `game_logic.py`; built last, purely I/O wiring

This order means Phase 1 milestones map naturally to the dependency graph: DB → services → controller → CLI.

## Sources

- Controller-Service-Repository pattern: well-established layered architecture pattern; PRIMARY confidence from project requirement itself (PROJECT.md explicitly mandates this pattern and file layout)
- `mysql-connector-python` `dictionary=True` cursor: official MySQL connector documentation
- CLI-to-web architecture upgrade rationale: standard "ports and adapters" / hexagonal architecture principle applied to this specific case
- Haversine formula as pure domain logic: standard geodesic distance calculation, no external library required for basic implementation

---
*Architecture research for: Python CLI strategy game (The Aviator) with MariaDB/MySQL*
*Researched: 2026-03-09*
