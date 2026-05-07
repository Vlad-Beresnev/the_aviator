# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-05-07)

**Core value:** Players can experience The Aviator game entirely in-browser — world map level select, browser action game, public scores.
**Current focus:** v0.1 Web MVP — COMPLETE

## Current Position

Milestone: v0.1 Web MVP (v0.1.0) — **COMPLETE**
Phase: 5 of 5 (Public Leaderboard) — Complete
Plan: 05-01 complete
Status: All phases unified — milestone complete
Last activity: 2026-05-07 — Phase 5 complete, v0.1 Web MVP shipped

Progress:
- Milestone: [██████████] 100%
- Phase 5: [██████████] 100%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete — v0.1 milestone done]
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
| L.divIcon for all map markers | Phase 3 | Avoids Leaflet's broken default icon asset resolution in Next.js bundler |
| markerClickedRef guard | Phase 3 | `stopPropagation` unreliable through react-leaflet-cluster — ref flag guards map click from clearing selection |
| dynamic(ssr:false) in "use client" | Phase 3 | Required by Next.js 16 — ssr:false only valid inside Client Components; Leaflet accesses window |
| window.location.href for Back to Map | Phase 4 | Phaser module-scope PluginManager survives SPA nav (router.push) — second game load fails; full reload required |
| earnedMoney ?? 0 in ResultOverlay | Phase 4 | speaker_fee undefined at runtime for some airports; TypeScript type doesn't match API reality |
| game.created_at migration | Phase 5 | Column didn't exist in CREATE TABLE — added idempotent ALTER TABLE; existing rows backfilled with migration timestamp |

### Deferred Issues

| Issue | Origin | Effort | Revisit |
|-------|--------|--------|---------|
| httpOnly cookie auth upgrade | Init | M | v0.2 |
| Real sprite artwork (replace rectangles) | Init | M | v0.2 |
| Mobile map usability | Init | S | v0.2 |
| login/register use `<a href>` not `<Link>` | Phase 2 | S | v0.2 |
| Token expiry not checked client-side | Phase 2 | S | v0.2 |
| game rows created before Phase 5 migration show same created_at | Phase 5 | XS | v0.2 cosmetic |

### Git State
Last commit: c8535af feat(05-public-leaderboard): v0.1 MVP complete
Branch: main
Feature branches merged: none
Note: Phase 4 game component files uncommitted (frontend/components/game/, frontend/components/auth/) — pre-existing from Phase 4 session

### Blockers/Concerns
None.

## Session Continuity

Last session: 2026-05-07
Stopped at: v0.1 Web MVP milestone complete — all 5 phases unified
Next action: /paul:complete-milestone to archive v0.1 and plan v0.2, or deploy to Hetzner VPS
Resume file: .paul/ROADMAP.md

---
*STATE.md — Updated after every significant action*
