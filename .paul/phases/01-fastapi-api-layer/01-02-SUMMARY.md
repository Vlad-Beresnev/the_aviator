---
phase: 01-fastapi-api-layer
plan: 02
subsystem: api
tags: [fastapi, jwt, mysql, pydantic]

requires:
  - phase: 01-01
    provides: FastAPI app, auth routes, get_current_user dependency, users table, DB migrations

provides:
  - GET /airports — JWT-protected list of all level airports with beaten/locked status
  - GET /airports/{ident} — single airport detail or 404
  - POST /game/start — idempotent: returns existing game or creates new one
  - GET /game/state — current game state for authenticated user
  - POST /game/complete-level — awards speaker_fee + increments global_awareness, 400 on repeat
  - GET /scores — public top-20 leaderboard sorted by money
  - db_manager.get_top_scores() — one row per player via MAX(id) GROUP BY subquery

affects: [02-nextjs-frontend-scaffold, 05-public-leaderboard]

tech-stack:
  added: []
  patterns:
    - "Thin route wrappers — routes call service/logic functions, no business logic in handlers"
    - "Idempotent POST for game start — POST /game/start returns existing game if found"
    - "Public endpoint without Depends() — GET /scores has no auth dependency"
    - "Error dict passthrough — game_logic returns {'error': str}, routes convert to HTTPException"

key-files:
  created:
    - api/routes/airports.py
    - api/routes/game.py
    - api/routes/scores.py
  modified:
    - api/main.py
    - db_manager.py

key-decisions:
  - "Idempotent /game/start: load existing game before creating new — prevents duplicate rows"
  - "get_top_scores uses MAX(id) subquery not MAX(money) — latest game row wins, not highest money ever"
  - "GET /scores is public by design — no Depends(get_current_user) — matches Phase 5 leaderboard requirement"

patterns-established:
  - "Thin route wrappers — routes call service/logic functions, no business logic in handlers"
  - "Error dict passthrough — game_logic returns {'error': str}, route converts to 400 HTTPException"

duration: ~15min
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 1 Plan 02: Data Routes Summary

**Three game endpoints + public scores wired into FastAPI — all existing Python game logic callable over HTTP.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15 min |
| Tasks | 3 completed |
| Files modified | 5 (3 created, 2 updated) |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Airport endpoints with auth | Pass | 200 array (451 airports), 401 no token, 404 nonexistent ident |
| AC-2: Game start/state idempotent | Pass | Returns money: 5000 on fresh start; same id on second POST |
| AC-3: Complete-level updates state and errors | Pass | Awards speaker_fee, 400 on repeat with "already beaten" message |
| AC-4: Scores public, sorted by money | Pass | 200 with no token, array sorted money DESC |

## Accomplishments

- All 6 Phase 1 endpoints wired — full API surface from ROADMAP.md scope is callable
- `get_top_scores` DB function uses correlated subquery to return one row per player
- Thin-wrapper pattern established: routes are pure HTTP adapters with no business logic

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `api/routes/airports.py` | Created | GET /airports + GET /airports/{ident}, both JWT-protected |
| `api/routes/game.py` | Created | POST /game/start (idempotent), GET /game/state, POST /game/complete-level |
| `api/routes/scores.py` | Created | GET /scores — public, no auth |
| `api/main.py` | Modified | Added three router includes |
| `db_manager.py` | Modified | Added `get_top_scores(limit)` before `delete_test_game` |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Idempotent POST /game/start | Prevents duplicate game rows on page refresh / double-click | Frontend can call freely without game-state guard |
| MAX(id) not MAX(money) in leaderboard query | Latest game row = current state; max money could surface stale inflated rows | Scores reflect current play, not all-time high |
| GET /scores public — no auth | Phase 5 leaderboard spec requires no login; simpler to decide now | Phase 5 can hit /scores directly with no auth header |

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- All Phase 1 API endpoints live and verified
- `api/routes/` module pattern established — Phase 2+ can add routes the same way
- JWT dependency wired — frontend can send `Authorization: Bearer <token>` to any protected route

**Concerns:**
- `GET /airports` returns 451 airports in one payload — fine for MVP, will need pagination if game expands to all 6,899 airports
- `game.name` used as join key (not `user_id`) — deferred migration logged in STATE.md

**Blockers:**
- None

---
*Phase: 01-fastapi-api-layer, Plan: 02*
*Completed: 2026-05-06*
