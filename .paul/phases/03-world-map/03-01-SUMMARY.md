---
phase: 03-world-map
plan: 01
subsystem: ui
tags: [react-leaflet, leaflet, leaflet-cluster, next-js, map, typescript]

requires:
  - phase: 02-nextjs-frontend-scaffold
    provides: authenticated route group, api.ts fetch wrapper, Next.js 16 App Router structure
  - phase: 01-fastapi-api-layer
    provides: GET /airports endpoint returning level airport data

provides:
  - Interactive world map at /map with 200-300 colored airport markers
  - Click-to-open airport detail panel with Play Level link
  - URL-persisted map zoom/center state

affects: [04-browser-action-game, 05-leaderboard]

tech-stack:
  added: [react-leaflet@5.0.0, leaflet@1.9.4, @types/leaflet@1.9.21, react-leaflet-cluster@4.1.3]
  patterns:
    - dynamic import with ssr:false for Leaflet (window access)
    - divIcon for markers (avoids Leaflet broken default icon in Next.js)
    - useRef guard for marker-vs-map click disambiguation
    - MapEvents inner component using useMapEvents for map-level event handling

key-files:
  created:
    - frontend/components/map/WorldMap.tsx
    - frontend/components/map/AirportPanel.tsx
  modified:
    - airport_service.py
    - frontend/lib/api.ts
    - frontend/app/(game)/map/page.tsx

key-decisions:
  - "divIcon for all markers: avoids Leaflet default icon broken asset paths in Next.js bundler"
  - "dynamic(ssr:false) in client component: required by Next.js 16 — ssr:false only valid in 'use client' files"
  - "markerClickedRef guard: stopPropagation unreliable through react-leaflet-cluster event layer"

patterns-established:
  - "Leaflet components must be dynamically imported with ssr:false — Leaflet accesses window"
  - "Map-level event handlers go in a dedicated inner component using useMapEvents, not on MapContainer"
  - "CSS for react-leaflet-cluster must be imported manually (v3+ breaking change)"

duration: ~45min
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 3 Plan 01: World Map (Level Select) Summary

**Interactive Leaflet world map at /map — 200-300 color-coded airport markers, click-to-open detail panel, URL-persisted zoom/center state.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~45 min |
| Tasks | 2 completed |
| Files modified | 5 |
| Checkpoint | 1 — approved |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Map renders with markers | Pass | Leaflet MapContainer fills viewport; ~200-300 airport markers visible |
| AC-2: Markers color-coded by game status | Pass | Yellow (open), green (beaten), red (locked) via L.divIcon |
| AC-3: Airport panel opens on marker click | Pass | Slide-in panel with name, city, level, stars, reward, Play Level button |
| AC-4: URL zoom/center persists | Pass | `?lat=X&lng=Y&zoom=Z` set via router.replace on moveend; parsed on mount |

## Accomplishments

- Added `latitude_deg`/`longitude_deg` to FastAPI `/airports` response — no DB schema change needed, fields already exist on airport records
- Created full `WorldMap.tsx` client component: clustered markers, color-coded divIcons, moveend URL sync, ref-based click guard
- Created `AirportPanel.tsx`: difficulty stars, status badge (beaten/locked/open), disabled Play button for locked airports, `<Link>` for playable airports
- Rewrote `map/page.tsx`: dynamic import (ssr:false), URL param parsing via useSearchParams, API fetch on mount

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `airport_service.py` | Modified | Added `latitude_deg`, `longitude_deg` to `get_level_airports()` output |
| `frontend/lib/api.ts` | Modified | Airport interface updated to match `/airports` response (`city`, `beaten`, `locked`, `level`, `difficulty`, `speaker_fee`) |
| `frontend/components/map/WorldMap.tsx` | Created | Leaflet map with clustered colored markers and URL state sync |
| `frontend/components/map/AirportPanel.tsx` | Created | Slide-in airport detail panel with Play Level link |
| `frontend/app/(game)/map/page.tsx` | Modified | Wires map + panel + URL state; dynamic import for SSR safety |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `L.divIcon` for all markers | Leaflet's default PNG icon has broken asset resolution in Next.js bundler | No icon URL config needed; markers render as styled divs |
| `dynamic(ssr:false)` in `"use client"` page | Next.js 16 requires `ssr:false` to live inside a Client Component | WorldMap never SSR'd — safe for Leaflet's `window` access |
| CSS imported manually in WorldMap.tsx | react-leaflet-cluster v3+ removed auto CSS import to prevent Next.js build issues | Required `leaflet/dist/leaflet.css` + cluster CSS imports at top of WorldMap |
| `markerClickedRef` guard | `stopPropagation` on Leaflet events does not reliably prevent map click through cluster layer | Ref set on marker click, checked+cleared in MapEvents click handler |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential fix, no scope creep |

**Total impact:** Single click-handling fix discovered at checkpoint; resolved in-session.

### Auto-fixed Issues

**1. Marker click event propagation through react-leaflet-cluster**
- **Found during:** Checkpoint human verify
- **Issue:** `e.originalEvent.stopPropagation()` in marker `eventHandlers.click` did not prevent the Leaflet map's `click` event from firing. Both events fired; React batched `setSelectedAirport(airport)` + `setSelectedAirport(null)`, final state was `null` — panel never appeared.
- **Fix:** Replaced `stopPropagation` with `markerClickedRef = useRef(false)` in `WorldMap`. Marker click sets `markerClickedRef.current = true` synchronously; `MapEvents.click` checks the flag, skips `onSelect(null)`, and resets it.
- **Files:** `frontend/components/map/WorldMap.tsx`

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Marker click not opening panel | Root cause: map click fired after marker click, resetting state. Fixed via ref guard (see Deviations). |

## Next Phase Readiness

**Ready:**
- `/map` route fully functional — players can browse airports and click Play Level to navigate to `/game/[ident]`
- `Airport` type in `api.ts` matches API response exactly — Phase 4 can use `api.getAirport(ident)` for game config
- URL state at `/map?lat=X&lng=Y&zoom=Z` — back-navigation from game will restore map position

**Concerns:**
- `/game/[ident]/page.tsx` is still a stub — Phase 4 must implement Phaser game there
- Phaser + Next.js SSR has known gotchas — `dynamic(ssr:false)` pattern (same as WorldMap) will be required
- Marker clustering means players must zoom in to click individual airports — acceptable for MVP, may need UX guidance text later

**Blockers:** None

---
*Phase: 03-world-map, Plan: 01*
*Completed: 2026-05-06*
