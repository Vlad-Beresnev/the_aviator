# Roadmap: The Aviator — Web Frontend

## Overview

Transform a working Python CLI game into a full browser experience: FastAPI wraps the existing Python game logic, Next.js delivers the UI, a React-Leaflet world map replaces the terminal level select, Phaser.js brings the action game to canvas, and a public leaderboard closes the loop. Deployed on Hetzner VPS via Docker Compose.

## Current Milestone

**v0.1 Web MVP** (v0.1.0)
Status: Complete
Phases: 5 of 5 complete

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | FastAPI API Layer | 2 | ✅ Complete | 2026-05-06 |
| 2 | Next.js Frontend Scaffold | 2 | ✅ Complete | 2026-05-06 |
| 3 | World Map (Level Select) | 1 | ✅ Complete | 2026-05-06 |
| 4 | Browser Action Game | 2 | ✅ Complete | 2026-05-07 |
| 5 | Public Leaderboard | 1 | ✅ Complete | 2026-05-07 |

## Phase Details

### Phase 1: FastAPI API Layer

**Goal:** All existing game logic is callable over HTTP — auth, airport data, game state CRUD, scores
**Depends on:** Nothing (first phase)
**Research:** Unlikely (wrapping existing modules, standard FastAPI patterns)

**Scope:**
- `api/main.py` — FastAPI app entry point
- `api/auth.py` — register, login, JWT creation/validation
- `api/routes/airports.py`, `game.py`, `scores.py`
- DB migration: `users` table + `game.name → game.user_id`
- Endpoints: POST /auth/register, POST /auth/login, GET /airports, GET /airports/{ident}, POST /game/start, GET /game/state, POST /game/complete-level, GET /scores

**Plans:**
- [x] 01-01: Foundation + Auth (DB migration, FastAPI scaffold, register/login/JWT)
- [x] 01-02: Data Routes (airports, game, scores) — depends on 01-01

---

### Phase 2: Next.js Frontend Scaffold

**Goal:** Working auth flow, protected routes, project structure in place
**Depends on:** Phase 1 (API auth endpoints)
**Research:** Unlikely (standard Next.js App Router patterns)

**Scope:**
- `bun create next-app frontend --typescript --tailwind --app`
- Route groups: `(auth)/login`, `(auth)/register`, `(game)/map`, `(game)/game/[ident]`, `(game)/leaderboard`
- `lib/api.ts` — typed fetch wrapper
- `lib/auth.tsx` — useAuth context + hook
- `middleware.ts` — redirect unauthenticated to /login
- JWT stored in localStorage (MVP)

**Plans:**
- [x] 02-01: Scaffold + route groups + lib/api.ts + CORS (complete)
- [ ] 02-02: Auth context + middleware (useAuth hook, JWT localStorage, protected routes)

---

### Phase 3: World Map (Level Select)

**Goal:** Interactive world map with 200–300 airport markers, color-coded by status, click shows play panel
**Depends on:** Phase 2 (frontend scaffold) + Phase 1 (GET /airports endpoint)
**Research:** Unlikely (React-Leaflet is established, clustering pattern is known)

**Scope:**
- `bun add react-leaflet leaflet @types/leaflet react-leaflet-cluster`
- Server-side filter: large_airport with goal records only (~200–300)
- Marker colors: yellow (open), green (beaten), red (locked)
- Click → slide-in panel: airport name, city, difficulty, reward, "Play Level" button
- URL params preserve map zoom/center state

**Plans:**
- [x] 03-01: Map foundation + airport panel + URL state

---

### Phase 4: Browser Action Game

**Goal:** Phaser.js game runs in-browser at /game/[ident], win/lose posts result back to API
**Depends on:** Phase 3 (map navigation) + Phase 1 (POST /game/complete-level)
**Research:** Likely (Phaser.js integration with Next.js/React has SSR gotchas)
**Research topics:** Phaser + Next.js App Router SSR compatibility, dynamic import pattern for canvas components

**Scope:**
- `bun add phaser && bun add -D @types/phaser`
- `<PhaserGame difficulty={n} battery={b} onComplete={handleResult} />` React component
- Phaser scenes: PreloadScene, GameScene (player plane, enemies, bullets, health, timer), ResultScene
- On victory: POST /game/complete-level → modal → redirect to map
- MVP sprites: colored rectangles (reuse sprite logic from `sprites.py` later)

**Plans:**
- [x] 04-01: Game Foundation — Phaser install, game page, PreloadScene + GameScene (full game loop)
- [x] 04-02: Result Flow + API — win/lose overlay, POST /game/complete-level, redirect to map

---

### Phase 5: Public Leaderboard

**Goal:** /leaderboard shows top 20 players by money, no login required, auto-refreshes
**Depends on:** Phase 4 (complete game loop) + Phase 1 (GET /scores)
**Research:** Unlikely (simple data fetch + table render)

**Scope:**
- Table: Rank | Player | Money | Levels Beaten | Last Active
- Calls GET /scores (public endpoint, no auth)
- Refresh button + auto-refresh every 60 seconds

**Plans:**
- [x] 05-01: Leaderboard page + extended scores query (created_at)

---

*Roadmap created: 2026-05-06*
*Last updated: 2026-05-07 — Phase 5 complete — v0.1 Web MVP shipped*
