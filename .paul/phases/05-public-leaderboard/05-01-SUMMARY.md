---
phase: 05-public-leaderboard
plan: 01
subsystem: ui
tags: [react, next.js, tailwind, mysql]

requires:
  - phase: 01-fastapi-api-layer
    provides: GET /scores public endpoint
  - phase: 02-nextjs-frontend-scaffold
    provides: Next.js route groups, lib/api.ts fetch wrapper, Score interface

provides:
  - Public leaderboard page at /leaderboard (no auth required)
  - Auto-refresh every 60s + manual Refresh button
  - game.created_at column + get_top_scores returning created_at

affects: []

tech-stack:
  added: []
  patterns:
    - setInterval auto-refresh with useEffect cleanup
    - Idempotent ALTER TABLE migration via _column_exists guard

key-files:
  created:
    - frontend/app/(game)/leaderboard/page.tsx
  modified:
    - db_manager.py
    - frontend/lib/api.ts

key-decisions:
  - "game.created_at migration: spec assumed column existed — added idempotent ALTER TABLE"

patterns-established:
  - "Leaderboard is static-shell + client hydration — 'use client' + useEffect, no dynamic(ssr:false) needed (no window access at import)"

duration: ~30min
started: 2026-05-07T00:00:00Z
completed: 2026-05-07T00:00:00Z
---

# Phase 5 Plan 01: Public Leaderboard Summary

**Public leaderboard page at /leaderboard — top 20 players by money, no auth, auto-refreshes every 60s — completing the v0.1 MVP.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~30 min |
| Tasks | 2 completed |
| Files modified | 3 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Table displays Rank/Player/Money/Awareness/Last Active | Pass | All 5 columns, up to 20 rows, money toLocaleString(), date via toLocaleDateString() |
| AC-2: Accessible without login | Pass | proxy.ts matcher is `/game/:path*` — /leaderboard is unprotected |
| AC-3: Auto-refresh every 60 seconds | Pass | setInterval(fetchScores, 60000) with clearInterval cleanup |
| AC-4: Manual Refresh button | Pass | onClick calls fetchScores immediately |

## Accomplishments

- Leaderboard page ships as the final v0.1 MVP feature — any visitor can see rankings without logging in
- game.created_at column added via idempotent migration; existing rows backfilled with insertion timestamp
- Score TypeScript interface extended with created_at, keeping API contract in sync with DB

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/app/(game)/leaderboard/page.tsx` | Created | Full leaderboard component — replaces stub |
| `db_manager.py` | Modified | Added created_at migration + updated get_top_scores SELECT |
| `frontend/lib/api.ts` | Modified | Score interface extended with created_at: string |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Scope additions | 1 | Necessary — without it the SELECT would error |

### Scope Additions

**1. game.created_at migration added to run_migrations()**
- **Found during:** Task 1 (Extend GET /scores)
- **Issue:** Plan spec said "add g.created_at to SELECT" but the column didn't exist in the game table schema — the CREATE TABLE in run_migrations() had no created_at column
- **Fix:** Added idempotent `_column_exists` guard + `ALTER TABLE game ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- **Files:** `db_manager.py`
- **Verification:** curl http://localhost:8000/scores returned created_at on all rows

## Next Phase Readiness

**Ready:**
- All 5 phases of v0.1 Web MVP are complete
- Full E2E flow available: register → login → map → click airport → play game → win → score appears on leaderboard

**Concerns:**
- game rows created before the migration all show the same created_at (time of migration run, not actual game time) — cosmetic for MVP, accurate for new games
- JWT stored in localStorage — httpOnly cookie upgrade deferred to post-v0.1

**Blockers:** None
