# Pitfalls Research

**Domain:** Python CLI strategy game with MySQL/MariaDB persistence, CSR architecture, planned web upgrade
**Researched:** 2026-03-09
**Confidence:** HIGH (well-documented failure modes in this exact stack; verified against known mysql-connector-python behavior and Python CLI game patterns)

---

## Critical Pitfalls

### Pitfall 1: Leaking a New Database Connection on Every Repository Call

**What goes wrong:**
Every call to a repository method opens a `mysql.connector.connect()`, executes the query, and never closes it (or closes it inside the method without using a context manager properly). After a few hundred game actions the MariaDB server hits `max_connections` and the game freezes or crashes with `Can't connect to MySQL server`.

**Why it happens:**
`mysql-connector-python` does not pool connections by default. Students and beginners treat `connect()` like a cheap file open — they call it inline inside the method and forget it. The game loop runs fast enough in testing (10 moves) that this never surfaces, then hits hard in a full playthrough.

**How to avoid:**
Create one connection at application startup in `db_manager.py` and pass it (or a connection factory / pool handle) into every repository. Alternatively use `mysql.connector.pooling.MySQLConnectionPool` with `pool_size=2` for Phase 1 (single-player, so 1-2 is enough). Close gracefully on exit via `atexit` or a context manager at the `main.py` level. Never call `connect()` inside a loop or per-query method.

**Warning signs:**
- Repository methods each contain their own `mysql.connector.connect()` call
- No `db_manager.py` that initializes a shared connection/pool
- `Too many connections` error after extended play sessions
- `config.py` stores DB credentials but nothing centralizes the connection object

**Phase to address:** Phase 1 (Foundation / DB layer) — must be correct from the first commit.

---

### Pitfall 2: Mixing Business Logic Into the Repository Layer

**What goes wrong:**
The repository method that fetches nearby airports also filters by battery range, applies the Haversine formula, and computes the recharge cost. When Phase 2 wraps the service layer in a Flask route, the repository is unreachable without the full game state object — there is no clean service boundary and the web layer has to re-implement or reimport game logic.

**Why it happens:**
It feels efficient to "do everything in one query." The SQL query already has coordinates, so it seems natural to compute distance there too. The distinction between "fetch raw data" and "apply game rules" collapses under time pressure.

**How to avoid:**
Repositories return raw data (airport rows as dicts/namedtuples). The service layer (`airport_service.py`, `player_service.py`) applies all game rules: distance filtering via Haversine, fee calculations, unlock checks. The `game_logic.py` orchestrates multi-step game events (e.g., forced landing sequence). This separation is the whole reason the CSR pattern is chosen — enforce it strictly.

**Warning signs:**
- A repository method accepts `player_battery` or `player_money` as a parameter
- Haversine formula appears at the SQL level via a stored procedure or raw SQL string with math
- Service methods do nothing except call one repository method and return the result unchanged
- Repository returns a Python dict with keys like `"can_fly": True`

**Phase to address:** Phase 1 (Service and Repository layer definition) — establish clear interface contracts before writing any business logic.

---

### Pitfall 3: Services Returning Mutable Game Objects Instead of Plain Dicts

**What goes wrong:**
`player_service.get_player()` returns a custom `Player` class instance. `game_logic.py` mutates its attributes directly (e.g., `player.battery -= cost`). Phase 2 Flask routes cannot serialize this object to JSON without custom encoders, and the mutation pattern makes it impossible to validate state before committing. The web upgrade requires rewriting the entire service interface.

**Why it happens:**
OOP patterns feel natural for a game. A `Player` object with methods seems cleaner than passing dicts around. The problem is invisible during Phase 1 because the CLI never serializes anything.

**How to avoid:**
Services return plain Python dicts (e.g., `{"id": 1, "name": "Vlad", "battery": 820, "money": 5000}`). The service layer computes the new state dict and calls the repository to persist it — no in-place mutation of returned objects. Enforce it with a `# RULE: services return dicts, never mutable objects` comment at the top of each service file.

**Warning signs:**
- `player_service.py` imports a `Player` dataclass or class and returns instances of it
- `game_logic.py` calls `player.battery -= flight_cost` instead of computing a new dict
- Serialization is not considered until "Phase 2 prep" is started
- Any service method signature returns `-> Player` instead of `-> dict`

**Phase to address:** Phase 1 (Service layer design) — the return type contract is the most load-bearing Phase 2 enabler.

---

### Pitfall 4: No Transaction Wrapping on Multi-Step Game State Updates

**What goes wrong:**
A flight action updates three rows: `game.battery_used`, `game.money`, `airport.is_unlocked`. If the process crashes or the DB connection drops between the second and third UPDATE, the database is in an inconsistent state — player has spent money but airport is not unlocked. On next load, the game presents the player at a "visited but locked" airport.

**Why it happens:**
Beginners write three separate `cursor.execute()` calls with `connection.commit()` after each one. This works in happy-path testing. The inconsistency only surfaces on crashes or restarts during development.

**How to avoid:**
Wrap multi-step game actions in explicit transactions. Begin with `connection.start_transaction()` (or rely on `autocommit=False`, the default), execute all related UPDATEs, then `connection.commit()`. Wrap in `try/except` with `connection.rollback()` on failure. Repository methods for composite game actions should accept a `connection` parameter so the transaction spans repositories without re-opening.

**Warning signs:**
- Each repository method calls `connection.commit()` at its own end
- No `try/except/rollback` pattern anywhere in repository code
- `autocommit=True` set on the connection (disables transaction control entirely)
- "Inconsistent game state" bugs appear after ctrl-C during playtesting

**Phase to address:** Phase 1 (Repository layer) — add transaction wrapping at the same time as writing the first multi-table operation.

---

### Pitfall 5: Storing DB Credentials in config.py Committed to Git

**What goes wrong:**
`config.py` contains `DB_HOST`, `DB_USER`, `DB_PASSWORD` as hardcoded strings. The file is committed to the repository. In an academic context this is a grade risk (plagiarism detection, public repo exposure). In Phase 2 (web deployment), it becomes a real credential leak if the project is pushed to GitHub.

**Why it happens:**
`config.py` is the natural place to put configuration. Environment variables feel like "production overhead" for a school project. The `config.py` pattern is explicitly named in the module structure requirement, so students assume it means hardcoded values.

**How to avoid:**
`config.py` reads from environment variables with a fallback for local dev: `DB_PASSWORD = os.environ.get("DB_PASSWORD", "localdevpassword")`. Add `config.py` to `.gitignore` OR use a `.env` file with `python-dotenv` (already common in Flask projects, making Phase 2 transition natural). The module structure requirement does not mandate hardcoded values — it just names the file.

**Warning signs:**
- `config.py` contains a literal password string
- No `.env` or `.env.example` file exists
- No `.gitignore` entry for `config.py` or `*.env`
- README instructs cloners to "edit config.py with your DB credentials"

**Phase to address:** Phase 1 (Project setup / first commit) — must be correct before the first `git push`.

---

### Pitfall 6: Input Validation Living in game_logic.py Instead of a Dedicated Layer

**What goes wrong:**
The main game loop in `main.py` (or `game_logic.py`) validates raw CLI input inline: checking if the user's airport choice is an integer, if it's in the valid range, if the player has enough battery. Phase 2 Flask routes need the same validation but can't reuse the CLI validation code because it's entangled with `input()` calls and `print()` statements.

**Why it happens:**
For a CLI, input validation and display are tightly coupled — you `input()`, validate, then `print()` the error. It seems natural to keep them together. The validation logic gets buried in the REPL loop.

**How to avoid:**
Separate validation into two distinct layers:
1. **Input parsing** (CLI-specific, in `main.py`): convert raw string to typed value, handle ValueError.
2. **Game rule validation** (in service layer): "can this player fly to this airport?" returns a result dict with `{"valid": False, "reason": "insufficient_battery"}`. The service layer never calls `input()` or `print()`. Phase 2 Flask routes call the same service validation and translate the result dict to HTTP 400 responses.

**Warning signs:**
- Service methods call `print()` for any reason
- Service methods raise `ValueError` with user-facing strings (mixes validation with display)
- `game_logic.py` contains `while True: raw = input(...)` loops
- The words "Please enter" appear anywhere outside `main.py`

**Phase to address:** Phase 1 (Service layer design) — establish the no-print-in-services rule before writing any game actions.

---

### Pitfall 7: Haversine Distance Computed in Python on the Full Airport Table

**What goes wrong:**
On each "view nearby airports" action, the code fetches ALL airports from the database, then runs Python-side Haversine on every row to filter by battery range. With 3,000+ airports in a real airport dataset, this is a full table scan + O(n) Python computation per action. It's slow and it couples the service layer to a dataset-size assumption.

**Why it happens:**
"Fetch all, filter in Python" is the simplest mental model. SQL spatial functions feel advanced. The dev tests with 50 airports and it's fast enough.

**How to avoid:**
Use a bounding-box pre-filter in SQL: compute a lat/lon bounding box from the current position and max range, add `WHERE lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s` to the query. This cuts the result set by 90-95% before Python-side Haversine refines it. For Phase 1 this is sufficient. Add an index on `(lat, lon)` columns. Phase 2 can upgrade to MySQL spatial functions (`ST_Distance_Sphere`) if needed.

**Warning signs:**
- Repository method for nearby airports has no WHERE clause on coordinates
- `airport_service.py` runs `for airport in all_airports: if haversine(...) <= range`
- Slow "view airports" action (>500ms) appears during playtesting with the real dataset
- `SELECT * FROM airport` appears without a LIMIT or coordinate filter

**Phase to address:** Phase 1 (Airport service + repository) — fix at first implementation, not as an optimization later.

---

### Pitfall 8: No Separation Between "New Game" Init and "Load Game" Resume

**What goes wrong:**
The game startup always creates a new `game` row in the database. If the player quits and reopens the game, a second `game` row is created and the old progress is orphaned. There is no "continue" path. Alternatively, the code always loads the last game row — which means testing creates ghost game records that corrupt test runs.

**Why it happens:**
"New game" is the first feature implemented. "Continue" feels like a stretch goal. The distinction between `INSERT` (new game) and `SELECT` (load game) is deferred. Test data accumulates silently.

**How to avoid:**
Design the game session from the start with two explicit entry points: `create_new_game(player_name)` (INSERT + return game_id) and `load_game(game_id)` (SELECT). The CLI menu in `main.py` presents both options. Repositories always work against a specific `game_id`, never "the most recent row." Tests use explicit game_id fixtures and clean up after themselves.

**Warning signs:**
- `game_logic.py` always calls `INSERT INTO game` on startup without checking for existing games
- The `game` table accumulates dozens of rows during development
- "Load game" is listed as a Phase 2 feature
- Repository queries use `ORDER BY id DESC LIMIT 1` to find "the current game"

**Phase to address:** Phase 1 (Game initialization flow) — the save/load contract must be defined before the game loop is written.

---

### Pitfall 9: Phase 2 Web Upgrade Painful Due to print() Calls in Service Layer

**What goes wrong:**
This is the aggregated consequence of pitfalls 3 and 6. When a Flask route calls `player_service.fly_to_airport(game_id, airport_id)`, the terminal prints "Flying to London Heathrow..." and "Battery depleted by 320 units." These prints go to the server stdout — invisible to the web client. The service has implicit side effects the web layer cannot intercept.

**Why it happens:**
During CLI development, printing from the service layer feels like helpful debug output. It gradually becomes load-bearing ("I need to see this to know the game is working"). Nobody removes it because it doesn't break Phase 1.

**How to avoid:**
Services are pure data processors. They return result dicts that include display-relevant data: `{"success": True, "battery_before": 820, "battery_after": 500, "distance_km": 3200, "airport_name": "London Heathrow"}`. The CLI `main.py` formats and prints this dict. Phase 2 Flask routes serialize the same dict to JSON. Zero prints in any file except `main.py`.

**Warning signs:**
- Any `print()` call outside `main.py`
- Service methods that return `None` (implies side-effect-only design)
- "It prints the result" described as a service feature in code comments
- Functions named `display_status()` or `show_airports()` living in service files

**Phase to address:** Phase 1 (Entire implementation) — enforce as a code review rule from day one.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcode `game_id=1` everywhere | Simpler first pass | Breaks multi-game support; must refactor all queries | Never — use a session variable from the start |
| `SELECT *` in repository queries | Less typing | Fragile to schema changes; returns unnecessary data to service layer | Never in production code; acceptable in throwaway prototypes only |
| Single `db.py` with module-level connection | Simple to import anywhere | Non-thread-safe; breaks under Flask's request-per-thread model in Phase 2 | Phase 1 only if a connection pool refactor is explicitly planned before Phase 2 starts |
| Inline SQL strings in service methods | Skips repository layer | SQL scattered across codebase; impossible to mock for testing | Never — all SQL lives in repository files only |
| `autocommit=True` on connection | No need to call `commit()` | Loses transaction atomicity on multi-step game actions | Never for this project |
| `except Exception: pass` to silence errors | Hides crashes during dev | Silent data corruption; impossible to debug production issues | Never |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `mysql-connector-python` cursor reuse | Call `cursor.fetchall()` then reuse the same cursor for another query without calling `cursor.close()` first — causes `Unread result found` error | Always close cursor after use, or use `cursor = connection.cursor(buffered=True)` |
| `mysql-connector-python` placeholders | Use `?` placeholder style (from sqlite3 or MariaDB native docs) — mysql-connector-python uses `%s` | Always use `%s`: `cursor.execute("SELECT * FROM airport WHERE id = %s", (airport_id,))` |
| MariaDB boolean columns | INSERT with Python `True/False` works, but SELECT returns `1/0` integers — `if airport["is_unlocked"] == True` can fail unexpectedly | Normalize at repository boundary: `bool(row["is_unlocked"])` when building the return dict |
| `mysql-connector-python` autocommit | Forgetting `connection.commit()` after INSERT/UPDATE because `autocommit` defaults to `False` — data appears to save during the session but vanishes on restart | Always call `connection.commit()` after writes, or use explicit transaction management with rollback |
| MariaDB `DECIMAL` lat/lon columns | Coordinates stored as `DECIMAL(9,6)` are returned as Python `Decimal` type (not `float`) — Haversine formula raises `TypeError` | Cast at repository boundary: `float(row["lat"])`, `float(row["lon"])` |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full airport table scan per action | "View nearby airports" takes 1-3 seconds | Bounding-box SQL WHERE clause + index on `(lat, lon)` | Real dataset of 3,000+ airports |
| N+1 query in "view airports" | One SELECT per airport to fetch its goal/fee info | JOIN `airport` to `goal` in one query | Noticeable at 20+ airports returned |
| No index on `game.player_id` | Slow game load as game table grows from testing | `CREATE INDEX idx_game_player ON game(player_id)` | After ~1,000 test game rows accumulate |
| Reconnecting on each action (Pitfall 1) | Game gradually slows; eventually crashes with connection error | Shared connection/pool initialized at startup | After ~100 actions or MariaDB's `wait_timeout` (default 8 hours) |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Hardcoded DB password in `config.py` | Credential exposure if repo is pushed to GitHub; academic integrity risk | Environment variables via `os.environ.get()` or `python-dotenv`; add `config.py` to `.gitignore` |
| String-formatting SQL queries (`f"SELECT ... WHERE id = {user_input}"`) | SQL injection — especially relevant when airport IDs come from user input | Always use parameterized queries: `cursor.execute(sql, (value,))` — no exceptions |
| No input length limit on player name | Database error on INSERT if name exceeds column length; potential log spam | Validate `len(name) <= 50` before INSERT; define `VARCHAR(50)` in schema |

---

## UX Pitfalls

Common user experience mistakes in CLI games.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Game crashes on non-integer input with Python traceback | Player sees confusing stack trace; game exits unexpectedly | Wrap all `int(input())` in `try/except ValueError` with re-prompt; never let exceptions bubble to the terminal |
| No confirmation before irreversible high-cost actions | Player accidentally drains budget or battery on misclick | Show cost summary and prompt "Confirm? (y/n)" for flight and recharge actions |
| Status display only shown after an action, not before | Player flies blind — doesn't know battery/money before choosing destination | Show full status at the top of every menu iteration, not only after state changes |
| Airport list includes unreachable airports | Player confused by airports they cannot afford to fly to | Filter to reachable airports only; optionally show a "too far" section separately |
| Cryptic ICAO codes with no name or country | Player has no idea where they are or where they're going | Always display: ICAO/IATA code + full airport name + city + country |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Forced landing:** Nearest airport lookup works even when ALL airports are beyond battery range — verify the fallback does not crash when the filtered result set is empty
- [ ] **Win condition:** Both win conditions (continent coverage AND money threshold) are checked after every action — verify neither is silently skipped when one is already met
- [ ] **Battery recharge:** Recharge cost is deducted from money AND money going negative is prevented — verify the service rejects recharge if player cannot afford it
- [ ] **is_unlocked persistence:** `UPDATE airport SET is_unlocked = 1` is committed and reflected in the next "view airports" call — verify with a full game restart cycle, not just in-session
- [ ] **New game vs load game:** Starting a second game does not overwrite or corrupt the first game's rows — verify with two concurrent game records in the table
- [ ] **Schema migration:** All required column additions (`money`, `global_awareness`, `battery_used`, `is_unlocked`) are applied to the existing airport database — verify against the real MariaDB instance, not a fresh test schema
- [ ] **global_awareness display:** The win progress metric appears in the status display after every action — verify it increments on lecture delivery and is visible before the player makes their next move

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Connection leak discovered late | LOW | Introduce `db_manager.py` with shared connection/pool; replace all per-method `connect()` calls — mechanical refactor, ~2 hours |
| Business logic embedded in repository layer | HIGH | Identify every game rule in SQL/repository; move each to service layer; add tests to verify behavior unchanged — high regression risk |
| Mutable objects returned from services | MEDIUM | Replace class instances with manual dict construction or `dataclasses.asdict()`; update all callers — no behavior change but widespread edits |
| No transactions on multi-step updates | MEDIUM | Refactor repositories to accept optional `connection` parameter; wrap callers in transaction blocks; test rollback paths explicitly |
| Credentials committed to git | HIGH | Rotate DB password immediately; rewrite git history with BFG Repo Cleaner; add `config.py` to `.gitignore` retroactively |
| `print()` calls throughout services | LOW | `grep -rn "print(" --include="*.py"` outside `main.py`; replace each with data in the return dict; update CLI caller to display — ~1 hour mechanical work |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Connection leak per repository call | Phase 1: DB layer setup | Run 200 consecutive game actions; confirm `SHOW STATUS LIKE 'Threads_connected'` stays at 1 |
| Business logic in repository | Phase 1: Layer boundary definition | Code review: no game parameters (battery, money) appear in repository method signatures |
| Mutable objects from services | Phase 1: Service interface design | All service return types are `dict` or `list[dict]`; no custom class instances returned |
| No transaction wrapping | Phase 1: Repository write methods | Simulate crash mid-flight via `Ctrl-C`; verify DB state is consistent on restart |
| Credentials in config.py | Phase 1: Project initialization | `git log --all -p -- config.py` contains no password literals |
| Input validation in wrong layer | Phase 1: Service layer design | No `print()` or `input()` calls exist outside `main.py` |
| Full airport table scan | Phase 1: Airport repository | "View airports" completes in <200ms with real dataset; `EXPLAIN` shows index use on lat/lon |
| No new/load game separation | Phase 1: Game initialization | Two game records coexist; loading game_id=2 shows correct independent state |
| Phase 2 print() side effects | Phase 1: Ongoing code review | `grep -rn "print(" --include="*.py" | grep -v "main.py"` returns zero results before Phase 2 begins |

---

## Sources

- `mysql-connector-python` official documentation: connection pooling behavior, cursor lifecycle, parameterized query `%s` syntax, `autocommit` default (`False`), `DECIMAL` type mapping — HIGH confidence
- Python CSR/Repository pattern: known behavior when object mutation replaces value returns — HIGH confidence from pattern documentation
- MariaDB/MySQL: `DECIMAL` to Python `Decimal` type coercion behavior documented in connector type mapping — HIGH confidence
- Haversine bounding-box optimization: standard geographic pre-filter pattern, widely documented — HIGH confidence
- `max_connections` exhaustion from unclosed connections: reproducible and documented in mysql-connector-python issue tracker behavior — HIGH confidence
- Phase 2 web upgrade pain from CLI-entangled logic: HIGH confidence from Flask/CLI migration patterns and CSR pattern documentation
- Credential leakage via `config.py`: common academic project antipattern with well-known consequences — HIGH confidence

---
*Pitfalls research for: Python CLI strategy game with MySQL/MariaDB, CSR architecture, Phase 2 web upgrade*
*Researched: 2026-03-09*
