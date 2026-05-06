# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-05-06)

**Core value:** Players can experience The Aviator game entirely in-browser — world map level select, browser action game, public scores.
**Current focus:** Phase 2 Plan 02-02 APPLY complete — ready for UNIFY

## Current Position

Milestone: v0.1 Web MVP (v0.1.0)
Phase: 2 of 5 (Next.js Frontend Scaffold) — Applied
Plan: 02-02 executed
Status: APPLY complete, ready for UNIFY
Last activity: 2026-05-06 — Executed 02-02-PLAN.md (3 tasks PASS, checkpoint approved)

Progress:
- Milestone: [██░░░░░░░░] 20%
- Phase 2: [████████░░] 80%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ○     [APPLY complete, ready for UNIFY]
```

## Accumulated Context

### Decisions

| Decision | Phase | Impact |
|----------|-------|--------|
| FastAPI + Next.js two-app structure | Init | Preserves Python game logic; all phases build on this split |
| React-Leaflet for world map | Init | Free tiles, no API key — Phase 3 locked in |
| Phaser.js for browser game | Init | Phase 4 locked in; watch for Next.js SSR gotchas |
| JWT in localStorage (MVP) | Init | Phase 2 auth strategy — upgrade to httpOnly cookies post-v0.1 |
| Next.js 16 async params | Phase 2 | `params` in dynamic routes is `Promise<{...}>` — must be awaited in all dynamic pages |
| Next.js 16 proxy.ts (not middleware.ts) | Phase 2 | Route guard file is proxy.ts, export is `proxy` — middleware.ts is deprecated in v16 |
| Dual-store auth (localStorage + plain cookie) | Phase 2 | `apiFetch` reads localStorage for Bearer token; proxy.ts reads `auth_token` cookie — both set by `auth.login()` |

### Deferred Issues

| Issue | Origin | Effort | Revisit |
|-------|--------|--------|---------|
| httpOnly cookie auth upgrade | Init | M | Post v0.1 ship |
| Real sprite artwork (replace rectangles) | Init | M | Phase 4 polish or v0.2 |
| Mobile map usability | Init | S | After leaderboard ships |
| login/register use <a href> not <Link> | Phase 2 | S | When UI is built in later phases |

### Git State
Last commit: c9a4118
Branch: main
Feature branches merged: none
Uncommitted: Full Phase 2 work (both plans) — commit during UNIFY/transition

### Blockers/Concerns
None.

## Session Continuity

Last session: 2026-05-06
Stopped at: APPLY complete for 02-02 (checkpoint approved)
Next action: Run /paul:unify .paul/phases/02-nextjs-frontend-scaffold/02-02-PLAN.md
Resume file: .paul/phases/02-nextjs-frontend-scaffold/02-02-PLAN.md

---
*STATE.md — Updated after every significant action*
