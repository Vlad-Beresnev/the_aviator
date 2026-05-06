---
phase: 01-fastapi-api-layer
plan: 01
subsystem: auth
tags: [fastapi, jwt, bcrypt, mysql, python-jose]

requires: []

provides:
  - FastAPI app scaffold (api/main.py, api/deps.py) running from project root
  - JWT auth: POST /auth/register (201 + token), POST /auth/login (200 + token)
  - get_current_user dependency (Depends) for protecting any route
  - DB migration: users table + nullable game.user_id column
  - bcrypt password hashing via bcrypt 5.x directly

affects:
  - 01-02 (data routes depend on get_current_user and app.include_router pattern)
  - All future phases that add routes to the FastAPI app

tech-stack:
  added: [fastapi==0.115.0, uvicorn[standard]==0.34.0, bcrypt==5.0.0, python-jose[cryptography]==3.3.0]
  patterns:
    - FastAPI lifespan context manager for DB migrations on startup
    - OAuth2PasswordBearer + Depends(get_current_user) for route protection
    - Direct bcrypt.hashpw/checkpw (no passlib wrapper)

key-files:
  created: [api/main.py, api/deps.py, api/auth.py, api/__init__.py, api/routes/__init__.py]
  modified: [db_manager.py, requirements.txt, .env.example]

key-decisions:
  - "Use bcrypt directly instead of passlib — passlib unmaintained and incompatible with bcrypt 4.x+"
  - "game.user_id column nullable — CLI backward compat; username (=game.name) is the join key in MVP"
  - "Run uvicorn from project root so db_manager/config imports resolve without path manipulation"

patterns-established:
  - "api/ package at project root — all uvicorn invocations use uvicorn api.main:app from root"
  - "db_manager._get_connection() used directly in route files — acceptable for MVP, upgrade if project scales"
  - "JWT payload: {sub: username, exp: utc+7days}, HS256 via python-jose"

duration: ~25min
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 1 Plan 01: Foundation + Auth Summary

**FastAPI app scaffold with JWT register/login, bcrypt password hashing, and DB migration adding users table and game.user_id column.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~25 min |
| Tasks | 3 completed |
| Files modified | 8 |
| Deviations | 1 (auto-fixed) |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: DB migration adds users table and game.user_id | Pass | Confirmed via MySQL SHOW TABLES / SHOW COLUMNS; idempotent on restart |
| AC-2: POST /auth/register creates user and returns JWT | Pass | 201 + token; 409 on duplicate username |
| AC-3: POST /auth/login authenticates and returns JWT | Pass | 200 on correct creds; 401 on wrong password |
| AC-4: JWT dependency rejects invalid tokens | Pass | get_current_user raises 401 for invalid/empty tokens |

## Accomplishments

- FastAPI app boots from project root with `uvicorn api.main:app`, runs migrations on startup via lifespan
- Auth round-trip verified: register → login → token; duplicate username → 409; wrong password → 401
- `get_current_user` dependency ready to protect any route in plan 01-02+

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `api/__init__.py` | Created | Python package marker |
| `api/main.py` | Created | FastAPI app, lifespan (migrations), health endpoint, auth router |
| `api/deps.py` | Created | JWT decode → get_current_user Depends() |
| `api/auth.py` | Created | POST /auth/register, POST /auth/login |
| `api/routes/__init__.py` | Created | Python package marker for routes subpackage |
| `db_manager.py` | Modified | Appended users table + game.user_id migration to run_migrations() |
| `requirements.txt` | Modified | Added fastapi, uvicorn, bcrypt, python-jose |
| `.env.example` | Modified | Added JWT_SECRET placeholder |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| `bcrypt` directly instead of `passlib` | `passlib` (last released 2020) incompatible with `bcrypt` 4.x+: `__about__.__version__` removed, internal `detect_wrap_bug` test fails at runtime | All password ops use `bcrypt.hashpw` / `bcrypt.checkpw`; no passlib wrapper |
| `game.user_id` nullable, no FK | CLI backward compat — existing game rows have no user_id; username = game.name is the join key in MVP | Plan 01-02 game routes use `player_service.load_player_game(username)` |
| `uvicorn api.main:app` from project root | `db_manager`, `config`, `airport_service` etc. live at root; running from inside api/ breaks imports | All deployment docs and Docker CMD must reflect this |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential fix, no scope change |

### Auto-fixed Issues

**1. Dependency: passlib replaced with bcrypt directly**
- **Found during:** Task 3 (auth endpoints) — first register call
- **Issue:** `passlib[bcrypt]==1.7.4` raises `ValueError: password cannot be longer than 72 bytes` during internal `detect_wrap_bug` call; `bcrypt.__about__.__version__` also missing → `passlib` effectively non-functional with `bcrypt` 5.x
- **Fix:** Removed `passlib[bcrypt]` from requirements.txt; added `bcrypt==5.0.0` explicitly; replaced `CryptContext` calls with `bcrypt.hashpw` / `bcrypt.checkpw` directly
- **Files:** `api/auth.py`, `requirements.txt`
- **Verification:** POST /auth/register returns 201, POST /auth/login with correct/wrong creds returns 200/401

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `passlib` incompatible with `bcrypt` 5.x at runtime | Switched to `bcrypt` directly — simpler and more correct |

## Next Phase Readiness

**Ready:**
- `get_current_user` dependency fully functional — plan 01-02 can wrap all routes with `Depends(get_current_user)`
- `app.include_router(auth_router)` pattern established — plan 01-02 repeats for airports/game/scores routers
- `db_manager._get_connection()` usable directly in route files
- `api/routes/` subpackage exists and is importable

**Concerns:**
- `uvicorn api.main:app` must always run from project root — Docker CMD must match this; easy to get wrong
- JWT_SECRET defaults to "changeme" if env var missing — will need to set in .env before testing with real data

**Blockers:** None — plan 01-02 can proceed immediately.

---
*Phase: 01-fastapi-api-layer, Plan: 01*
*Completed: 2026-05-06*
