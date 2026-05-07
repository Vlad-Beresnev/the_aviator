# The Aviator — Web Frontend

## What This Is

A web frontend for The Aviator Python CLI game. FastAPI wraps the existing Python game logic (airport_service, game_logic, db_manager) and exposes a REST API with JWT auth. Next.js 14 (App Router, TypeScript, Bun) provides the browser interface: an interactive world map where airports are the level select screen, an in-browser action game built with Phaser.js, and a public leaderboard. All deployed on Hetzner VPS via Docker Compose + Nginx reverse proxy.

## Core Value

Players can experience The Aviator game entirely in-browser — no terminal needed — with a world map level select, browser-based action game, and public scores.

## Current State

| Attribute | Value |
|-----------|-------|
| Type | Application |
| Version | 0.1.0 |
| Status | Complete |
| Last Updated | 2026-05-07 |

## Requirements

### Core Features

- JWT-authenticated REST API wrapping all existing Python game logic
- Interactive world map with 200–300 airports as clickable level markers (color-coded by status)
- In-browser Phaser.js action game that posts results back to the API
- Public leaderboard (top 20 players by money, no login required)
- Auth flow: register, login, protected routes, JWT in localStorage

### Validated (Shipped)
- ✓ JWT-authenticated REST API wrapping all Python game logic — Phase 1
  - POST /auth/register, POST /auth/login (bcrypt + JWT)
  - GET /airports, GET /airports/{ident} (JWT-protected)
  - POST /game/start (idempotent), GET /game/state, POST /game/complete-level
  - GET /scores (public leaderboard endpoint)
- ✓ Next.js 16 frontend scaffold with working auth flow — Phase 2
  - Route groups (auth)/ and (game)/, 5 stub pages + root redirect
  - lib/api.ts typed fetch wrapper for all 8 Phase 1 endpoints
  - AuthContext (localStorage + cookie dual-store), useAuth hook
  - proxy.ts route guard — /map and /game/* require auth
  - Working login/register forms
- ✓ Interactive world map with colored airport markers and level-select panel — Phase 3
  - React-Leaflet map at /map with ~200-300 clustered airport markers
  - Markers color-coded: yellow (open), green (beaten), red (locked)
  - Click-to-open panel: name, city, level, difficulty stars, reward, Play Level link
  - URL-persisted zoom/center state (?lat=X&lng=Y&zoom=Z)
  - GET /airports now includes latitude_deg, longitude_deg
- ✓ In-browser Phaser.js action game with full play loop — Phase 4
  - Phaser 4.1.0 game at /game/[ident]: player, 3 enemy variants, bullets, collision, HUD
  - Win condition: survive 75s → POST /game/complete-level → Victory overlay
  - Lose condition: battery=0 → Mission Failed overlay (no API call)
  - Overlay navigation: Back to Map (full-page reload) + Try Again (reload) buttons
- ✓ Public leaderboard showing top 20 players without login — Phase 5
  - /leaderboard page: Rank | Player | Money | Awareness | Last Active table
  - Auto-refresh every 60s + manual Refresh button
  - game.created_at column added; Score interface extended

### Active (In Progress)
None — all v0.1 MVP features shipped.

### Planned (Next)
None — v0.1 MVP complete.

### Out of Scope
- Rewriting Python game logic in TypeScript — ~500 lines of working code, no user-facing benefit
- Mobile-first design in MVP — mobile map usability is polish phase
- Real sprite artwork in MVP — colored rectangles work as placeholder sprites

## Target Users

**Primary:** Players who want to play The Aviator without a terminal
- Familiar with the CLI game or new browser players
- Expects a web game: click to play, no setup required

**Secondary:** Spectators checking the public leaderboard without an account

## Context

**Technical Context:**
Existing Python codebase is fully functional: `airport_service.py`, `game_logic.py`, `db_manager.py`, `action_game.py`, `player_service.py`. MySQL holds 6,899 airports with lat/lon and all game state. The browser game (Phaser.js) is the only unavoidable rewrite from Python/Pygame.

**Business Context:**
Solo project on Hetzner VPS. Self-hosted deployment. Fixed infrastructure — no cloud spend beyond existing VPS.

## Constraints

### Technical Constraints
- Existing Python game logic must not be rewritten — FastAPI wraps it
- MySQL is the existing database — no migration to a new DB
- Phaser.js required for browser game (Pygame cannot run in browser)
- JWT auth required (localStorage to start, httpOnly cookies as upgrade)
- Airport markers must cluster — 200–300 large airports need react-leaflet-cluster

### Business Constraints
- Solo developer — no team to review
- Self-hosted on Hetzner VPS (Docker Compose + Nginx)
- No API key budget — OpenStreetMap tiles only (React-Leaflet free tier)

### Compliance Constraints
- Password storage: bcrypt hashing via passlib (no plaintext)

## Key Decisions

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| FastAPI + Next.js (two-app structure) | Preserves ~500 lines of working Python game logic; only the browser game requires rewrite | 2026-05-06 | Active |
| React-Leaflet for world map | Free (OpenStreetMap tiles), no API key, React-native integration, marker clustering support | 2026-05-06 | Active |
| Phaser.js for browser game | Industry-standard game framework, TypeScript support, handles sprite rendering + collision | 2026-05-06 | Active |
| JWT in localStorage (MVP) | Simple to implement; upgrade to httpOnly cookies post-MVP | 2026-05-06 | Active |
| Next.js 16 proxy.ts (not middleware.ts) | Next.js 16 renamed route guard file; export is `proxy`; middleware.ts is deprecated | 2026-05-06 | Active |
| Dual-store auth (localStorage + cookie) | apiFetch reads localStorage for Bearer; proxy.ts (Edge Runtime) reads cookie — login() syncs both | 2026-05-06 | Active |
| Filter to large_airport only (~200–300) | All 6,899 airports would overwhelm the map; only those with goal records are levels | 2026-05-06 | Active |
| L.divIcon for map markers | Leaflet's default PNG icon has broken asset resolution in Next.js bundler; divIcon renders pure HTML/CSS | 2026-05-06 | Active |
| markerClickedRef guard for click handling | react-leaflet-cluster makes stopPropagation unreliable; ref flag set on marker click prevents map click from clearing selection | 2026-05-06 | Active |
| dynamic(ssr:false) in Client Component for Leaflet | Next.js 16 requires ssr:false inside "use client" component; Leaflet accesses window at import time | 2026-05-06 | Active |
| window.location.href for game→map navigation | router.push (SPA nav) doesn't clear Phaser's module-scope PluginManager — second game load fails with "Core Plugins missing"; full-page nav is required | 2026-05-07 | Active |
| earnedMoney ?? 0 in ResultOverlay | speaker_fee is undefined at runtime for some airports despite TypeScript number type — API schema drift; guard prevents crash | 2026-05-07 | Active |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Phase 1: API responds | `curl localhost:8000/airports` returns airport JSON | 451 airports, all endpoints verified | ✅ Complete |
| Phase 2: Auth flow | Register → login → access /map (redirect if not logged in) | register, login, proxy redirect all verified | ✅ Complete |
| Phase 3: Map loads | 200–300 markers visible, click shows airport panel | Markers visible, panel opens on click, URL state persists | ✅ Complete |
| Phase 4: Game playable | Navigate to /game/EGLL, canvas renders, can win/lose | Full game loop: play → result overlay → map | ✅ Complete |
| Phase 5: Leaderboard | /leaderboard shows top players without login | Table renders, auto-refreshes, no auth required | ✅ Complete |
| E2E flow | Register → Login → Map → Click airport → Play → Win → Score updated | Full path available — all 5 phases shipped | ✅ Complete |

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend Framework | Next.js 14 (App Router) | TypeScript, Tailwind CSS, Bun runtime |
| Game Engine | Phaser.js | Browser canvas game, TypeScript support |
| Map Library | React-Leaflet + react-leaflet-cluster | OpenStreetMap tiles, no API key |
| Backend | FastAPI + Uvicorn | Wraps existing Python game modules |
| Auth | python-jose (JWT) + passlib (bcrypt) | JWT in localStorage MVP |
| Database | MySQL (existing) | +users table; game.name → game.user_id |
| Containerization | Docker Compose | nginx, nextjs, fastapi, mysql services |
| Reverse Proxy | Nginx + Let's Encrypt | / → Next.js :3000, /api → FastAPI :8000 |
| VPS | Hetzner | Existing server |

## Links

| Resource | URL |
|----------|-----|
| Repository | (local — no remote yet) |

---
*PROJECT.md — Updated when requirements or context change*
*Last updated: 2026-05-07 after Phase 5 — v0.1 Web MVP complete*
