# Phase 1: Foundation - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Database schema is correct, credentials are safe, and the module skeleton enforces layer boundaries before any game logic is written. No game logic, navigation, or CLI menus in this phase — only the foundation that every other phase rests on.

</domain>

<decisions>
## Implementation Decisions

### Starting airport selection
- Filter to `type='large_airport'` only when selecting a starting airport (~500 large airports globally)
- Starting airport is fixed: **SFO — San Francisco International (ident: KSFO, iata_code: SFO)** — always the same for every new game
- Store the starting airport ident as a constant in `config.py`

### Load game identification
- "Continue existing game" asks the player for their name, then loads the most recent row in the `game` table with that player name (ORDER BY id DESC LIMIT 1)
- If no record is found for the entered name: show a clear error message ("No game found for [name]") and re-prompt — do NOT auto-create a new game on continue
- New game and continue game are separate explicit flows from the startup menu

### Claude's Discretion
- Migration safety: ALTER TABLE statements should be idempotent where possible (check if column exists before adding) — dev workflow should not crash on re-run
- `db/populatedb.py` credentials: leave as-is for now (run-once manual script) — not updated to .env in Phase 1
- Exact module skeleton depth: stub functions with docstrings and pass/return {} placeholders are sufficient — no logic in Phase 1 stubs

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `db/lp_project_base.sql`: Airport data source — 6,899 airports, columns: id, ident, type, name, latitude_deg, longitude_deg, elevation_ft, continent, iso_country, iso_region, municipality, scheduled_service, gps_code, iata_code. Filter `type='large_airport'` for eligible airports. KSFO is in this dataset.
- `db/populatedb.py`: Reference for mysql-connector-python connection pattern (host: mysql.metropolia.fi, port: 3306)
- `high-level-plan.md`: ALTER TABLE statements already drafted — rename `co2_consumed → battery_used`, add `money INT DEFAULT 5000`, add `global_awareness INT DEFAULT 0`, add `is_unlocked BOOLEAN DEFAULT 0`

### Established Patterns
- `mysql-connector-python` is the required DB library (assignment constraint)
- Controller-Service-Repository pattern is mandatory from the first commit — db_manager.py handles all SQL, services return plain dicts only
- Credentials must come from `.env` file — never hardcoded in source

### Integration Points
- `config.py` → imported by `db_manager.py` (credentials) and `game_logic.py` (constants like MAX_BATTERY, STARTING_AIRPORT)
- `db_manager.py` → imported by all service modules
- All service modules → imported by `game_logic.py`
- `game_logic.py` → imported by `main.py` only

</code_context>

<specifics>
## Specific Ideas

- SFO (KSFO) as fixed starting airport — Silicon Valley / tech innovation framing fits the eco-aviation narrative
- `high-level-plan.md` has the exact ALTER TABLE SQL to use as reference for Phase 1 migrations

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-09*
