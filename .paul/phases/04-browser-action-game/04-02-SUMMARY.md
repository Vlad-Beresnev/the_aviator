---
phase: 04-browser-action-game
plan: 02
subsystem: ui
tags: [phaser, react, next.js, game-loop]

requires:
  - phase: 04-01
    provides: PhaserGame component with onComplete callback, GameScene firing victory/defeat events

provides:
  - ResultOverlay component (victory + defeat variants, full-screen)
  - Closed play loop: game → result overlay → map or retry
  - POST /game/complete-level called on victory only

affects: [05-public-leaderboard]

tech-stack:
  added: []
  patterns:
    - "window.location.href for Back to Map — full reload clears Phaser global state"
    - "earnedMoney ?? 0 guard — API may return undefined for speaker_fee"

key-files:
  created: [frontend/components/game/ResultOverlay.tsx]
  modified: [frontend/app/(game)/game/[ident]/page.tsx]

key-decisions:
  - "window.location.href instead of router.push for Back to Map — Phaser module-global state not cleared by SPA navigation"
  - "earnedMoney ?? 0 guard — speaker_fee undefined at runtime for some airports despite number type"

patterns-established:
  - "Game navigation uses window.location.href, not Next.js router — required for Phaser lifecycle correctness"

duration: ~30min
started: 2026-05-07T00:00:00Z
completed: 2026-05-07T00:00:00Z
---

# Phase 4 Plan 02: Result Flow + API Summary

**Victory/defeat overlay wired to game — win posts to /game/complete-level, both overlays navigate back to map or retry with correct full-page reload for Phaser cleanup.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~30 min |
| Tasks | 3 completed (2 auto + 1 checkpoint) |
| Files modified | 2 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Victory posts result and shows overlay | Pass | api.completeLevel called once on win; overlay shows "Victory!", airport name, earned money |
| AC-2: Defeat shows overlay without API call | Pass | completeLevel not called on defeat; "Mission Failed" overlay with Try Again + Back to Map |
| AC-3: Overlay navigation works | Pass | Back to Map → /map (full reload); Try Again → window.location.reload() |

## Accomplishments

- `ResultOverlay.tsx` built as pure React component — fixed full-screen overlay, inline styles, victory and defeat variants
- `handleComplete` in game page wired async: API call on victory (try/catch so network errors don't strand the user), then `setResult` regardless
- Both navigation buttons use full-page navigation (`window.location.href`) to guarantee Phaser's global PluginManager state is cleared before any re-initialization

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/components/game/ResultOverlay.tsx` | Created | Full-screen victory/defeat overlay with Back to Map + Try Again buttons |
| `frontend/app/(game)/game/[ident]/page.tsx` | Modified | result state, async handleComplete with API call, conditional overlay render |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `window.location.href = '/map'` instead of `router.push('/map')` | Phaser 3 stores global PluginManager state in module scope; SPA navigation doesn't clear it, causing "Core Plugins missing" on second game load | All game→map navigation uses full reload — slightly slower but Phaser-safe |
| `earnedMoney ?? 0` guard in ResultOverlay | API returns `undefined` for `speaker_fee` on some airports at runtime despite TypeScript typing it as `number` | Overlay never crashes on win; shows "+$0 earned" when fee not set |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 2 | Both discovered at checkpoint, fixed inline |
| Scope additions | 0 | — |
| Deferred | 0 | — |

**Total impact:** Essential runtime fixes discovered during human verification, no scope creep.

### Auto-fixed Issues

**1. Phaser "Core Plugins missing" on game replay**
- **Found during:** Checkpoint human-verify (defeat → Back to Map → replay)
- **Issue:** `router.push('/map')` is SPA navigation — Phaser's module-scope PluginManager state persists between navigations, causing constructor failure on second visit
- **Fix:** Changed `onBack` from `() => router.push('/map')` to `() => { window.location.href = '/map'; }` — full page navigation clears all JS state
- **Files:** `frontend/app/(game)/game/[ident]/page.tsx`, also removed unused `useRouter` import

**2. `earnedMoney.toLocaleString()` crash on victory**
- **Found during:** Checkpoint human-verify (victory path)
- **Issue:** `airport.speaker_fee` is `undefined` at runtime for some airports — TypeScript type says `number` but API omits the field
- **Fix:** `(earnedMoney ?? 0).toLocaleString()` in ResultOverlay
- **Files:** `frontend/components/game/ResultOverlay.tsx`

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Phaser global state not cleared by SPA navigation | Switched to full-page navigation for all game→map transitions |
| speaker_fee missing from some airport API responses | Runtime guard with ?? 0 |

## Next Phase Readiness

**Ready:**
- Full play loop complete: map → game → result → map
- POST /game/complete-level fires correctly on victory; game state updates server-side
- Phase 5 (leaderboard) can display scores accumulated through this loop

**Concerns:**
- `speaker_fee` being undefined for some airports suggests backend data quality gap — leaderboard money values may also be inconsistent
- Full-page reload on Back to Map means Next.js app state (auth context, etc.) re-initialises each time — currently fine for MVP

**Blockers:** None

---
*Phase: 04-browser-action-game, Plan: 02*
*Completed: 2026-05-07*
