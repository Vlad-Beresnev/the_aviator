---
phase: 04-browser-action-game
plan: 01
subsystem: ui
tags: [phaser, next.js, react, canvas, game-loop]

requires:
  - phase: 03-world-map
    provides: /game/[ident] page stub + airport API + navigation from map

provides:
  - Phaser 4 game loop fully playable at /game/[ident]
  - onComplete({victory, battery}) callback wired and ready for 04-02

affects: [04-02-result-flow]

tech-stack:
  added: [phaser@4.1.0]
  patterns:
    - dynamic import with ssr:false for Phaser in Next.js client component
    - programmatic texture generation via this.make.graphics() + generateTexture()
    - React↔Phaser bridge via game.registry (pass props as key/value store)
    - delta-time normalization — dt = delta / (1000/FPS) for frame-rate independence

key-files:
  created:
    - frontend/components/game/constants.ts
    - frontend/components/game/PhaserGame.tsx
    - frontend/components/game/scenes/PreloadScene.ts
    - frontend/components/game/scenes/GameScene.ts
  modified:
    - frontend/app/(game)/game/[ident]/page.tsx

key-decisions:
  - "Phaser 4.1.0 (not 3.x) — ships with own types; @types/phaser not needed"
  - "useParams() for ident in client component — documented Next.js 16 hook, not React.use(params)"
  - "cancelled guard in PhaserGame.tsx — prevents double-init on React StrictMode double-invoke"
  - "Manual rect intersection (Phaser.Geom.Intersects) over Arcade physics — simpler for this game"

patterns-established:
  - "All Phaser canvas components: dynamic import + ssr:false inside a 'use client' wrapper"
  - "All game magic numbers live in constants.ts — scenes import from there, never hardcode"
  - "Registry for React→Phaser data: game.registry.set() before scene boots"

duration: ~1 session
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 4 Plan 01: Browser Action Game — Foundation Summary

**Phaser 4 game loop ships at /game/[ident]: player, 3 enemy variants, bullets, collision, battery/timer/km HUD, 75s win + battery=0 lose, onComplete callback ready for 04-02.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~1 session |
| Tasks | 3 auto + 1 checkpoint |
| Files created | 4 new, 1 rewritten |
| TypeScript errors | 0 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Canvas renders | Pass | Phaser canvas fills viewport; scrolling starfield; player at bottom center |
| AC-2: Player movement and firing | Pass | WASD + arrows clamped to bounds; Space fires + auto-fire at 3× interval |
| AC-3: Enemy system | Pass | 3 variants spawn at top, drift/fire, difficulty+ramp scales with progress |
| AC-4: Collision and damage | Pass | Bullet hit = HIT_DAMAGE(50); body hit = HIT_DAMAGE×2(100); player bullet kills enemy |
| AC-5: Win/lose conditions | Pass | 75s elapsed → onComplete({victory:true}); battery=0 → onComplete({victory:false}) |
| AC-6: HUD accuracy | Pass | Battery (green→yellow→red), timer (blue→orange), km bar + text update each frame |

## Accomplishments

- Phaser 4.1.0 integrated into Next.js 16 App Router with zero SSR errors via dynamic import + `ssr:false`
- Complete game loop matching Python `action_game.py` — difficulty ramp, passive drain, delta-time normalization
- React↔Phaser data bridge via registry — clean separation with no global state

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/components/game/constants.ts` | Created | All 13 game constants (mirrors config.py) |
| `frontend/components/game/PhaserGame.tsx` | Created | React wrapper: dynamic import, cancelled guard, registry setup |
| `frontend/components/game/scenes/PreloadScene.ts` | Created | Programmatic textures: player, 3 enemy variants, 2 bullet types |
| `frontend/components/game/scenes/GameScene.ts` | Created | Full game loop: BG, movement, spawning, firing, collision, HUD, win/lose |
| `frontend/app/(game)/game/[ident]/page.tsx` | Rewritten | "use client", useParams, startGame+getAirport+getGameState, renders PhaserGameDynamic |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `useParams()` over `React.use(params)` | Next.js 16 docs prescribe `useParams` for client components | page.tsx follows official hook pattern |
| `@types/phaser` skipped | Phaser 4 ships own declarations (`types/phaser.d.ts`) | No extra package needed |
| `cancelled` guard in PhaserGame | React StrictMode double-invokes useEffect; guard prevents double Phaser.Game init | Clean mount/unmount in dev and prod |
| Manual rect intersection over Arcade physics | Simpler for 2D shooter with no complex physics needs | No physics bodies needed; cleaner code |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-adapted | 3 | All non-breaking; improvements or equivalents |
| Deferred | 0 | — |

**Total impact:** Minor adaptations only — no scope change, no deferred work.

### Auto-adapted

**1. `@types/phaser` not installed**
- Found during: Task 1
- Issue: Plan said `bun add -D @types/phaser` — package is Phaser 3 era; Phaser 4 ships own types
- Fix: Skipped install; Phaser 4 types load from `node_modules/phaser/types/phaser.d.ts`
- Verification: tsc --noEmit passes with 0 errors

**2. `useParams()` instead of `React.use(params)`**
- Found during: Task 2
- Issue: Plan specified `React.use(params)` for client component; Next.js 16 docs show `useParams()` as the client hook
- Fix: Used `useParams<{ ident: string }>()` from `next/navigation`
- Verification: Page loads correctly; ident extracted from URL

**3. `cancelled` guard + `gameRef` added to PhaserGame**
- Found during: Post-task linter pass
- Issue: Async init without cancel guard causes double Phaser.Game creation on React StrictMode unmount+remount
- Fix: `cancelled` boolean + `gameRef.current` for cleanup — prevents double init, no behavioral change in production
- Verification: tsc clean; dev server hot-reload shows single game instance

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| tsc failed after Task 2 — PreloadScene/GameScene not found | Expected dependency — Task 2 imports Task 3's files. Resolved by creating scenes in Task 3 |

## Next Phase Readiness

**Ready:**
- `/game/[ident]` fully playable — 04-02 can wire result overlay immediately
- `handleComplete(result)` stub in page.tsx is the integration point — replace `console.log` with `api.completeLevel(ident)` + overlay
- `api.completeLevel(ident)` already exists in `frontend/lib/api.ts:83`
- `onComplete` delivers `{ victory: boolean, battery: number }` — both fields available to result UI

**Concerns:**
- None

**Blockers:**
- None

---
*Phase: 04-browser-action-game, Plan: 01*
*Completed: 2026-05-06*
