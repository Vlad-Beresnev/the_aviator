# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-05-06)

**Core value:** Players can experience The Aviator game entirely in-browser — world map level select, browser action game, public scores.
**Current focus:** Phase 4 — Browser Action Game (Phaser.js)

## Current Position

Milestone: v0.1 Web MVP (v0.1.0)
Phase: 4 of 5 (Browser Action Game) — Not started
Plan: Not started
Status: Ready to plan Phase 4
Last activity: 2026-05-06 — Phase 3 complete, transitioned to Phase 4

Progress:
- Milestone: [██████░░░░] 60%
- Phase 4: [░░░░░░░░░░] 0%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ○        ○        ○     [Phase 4 — ready to plan]
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

### Deferred Issues

| Issue | Origin | Effort | Revisit |
|-------|--------|--------|---------|
| httpOnly cookie auth upgrade | Init | M | Post v0.1 ship |
| Real sprite artwork (replace rectangles) | Init | M | Phase 4 polish or v0.2 |
| Mobile map usability | Init | S | After leaderboard ships |
| login/register use `<a href>` not `<Link>` | Phase 2 | S | When UI gets styled in later phases |
| Token expiry not checked client-side | Phase 2 | S | Post-MVP auth hardening |

### Git State
Last commit: 9585cba
Branch: main
Feature branches merged: none

### Blockers/Concerns
None.

## Session Continuity

Last session: 2026-05-06
Stopped at: Phase 3 complete, transitioned to Phase 4
Next action: /paul:plan for Phase 4 (Browser Action Game — Phaser.js)
Resume file: .paul/ROADMAP.md

---
*STATE.md — Updated after every significant action*
