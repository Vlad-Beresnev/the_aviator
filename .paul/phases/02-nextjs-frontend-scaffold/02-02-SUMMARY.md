---
phase: 02-nextjs-frontend-scaffold
plan: 02
subsystem: auth
tags: [nextjs, react-context, jwt, localStorage, cookie, proxy, auth-flow]

requires:
  - phase: 02-nextjs-frontend-scaffold/02-01
    provides: lib/api.ts with api.login() and api.register() — called by login/register forms

provides:
  - AuthContext with login/logout — dual-store (localStorage + plain cookie)
  - proxy.ts protecting /map and /game/* routes
  - Working login + register forms (Client Components)
affects: [03-world-map, 04-browser-game, 05-leaderboard]

tech-stack:
  added: []
  patterns: [React Context + custom hook, dual-store JWT (localStorage + cookie), Next.js 16 proxy.ts]

key-files:
  created: [frontend/lib/auth.tsx, frontend/proxy.ts]
  modified: [frontend/app/layout.tsx, frontend/app/(auth)/login/page.tsx, frontend/app/(auth)/register/page.tsx]

key-decisions:
  - "proxy.ts not middleware.ts — Next.js 16 renamed the route guard file; export is 'proxy', not 'middleware'"
  - "Dual-store auth: login() writes to localStorage (for apiFetch Bearer) AND plain cookie (for proxy.ts to read)"
  - "AuthProvider in root layout.tsx — Server Component rendering Client Component boundary works as intended"

patterns-established:
  - "useAuth() hook: always call inside AuthProvider; throws if called outside"
  - "All Client Component pages needing auth state: import useAuth from @/lib/auth"
  - "All route protection is in proxy.ts matcher — not in individual page components"

duration: ~10min
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 2 Plan 02: Auth Context + Proxy Summary

**AuthProvider (localStorage + cookie dual-store), working login/register forms, and proxy.ts route guard — Phase 2 fully delivers a working auth flow with protected game routes.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~10 min |
| Started | 2026-05-06 |
| Completed | 2026-05-06 |
| Tasks | 3 auto + 1 checkpoint |
| Files modified | 5 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: AuthContext stores and reads JWT | Pass | localStorage + cookie set on login(), cleared on logout(); useAuth() returns current token |
| AC-2: Proxy protects game routes | Pass | proxy.ts matcher covers /map and /game/*; /login, /register, /leaderboard unaffected |
| AC-3: Login/register forms complete auth flow | Pass | Human checkpoint approved — register, login, error display, public routes all verified |

## Accomplishments

- Working auth flow: register → token stored → /map loads; login → same flow
- `proxy.ts` (Next.js 16 route guard) redirects unauthenticated users away from /map and /game/*
- `useAuth()` hook available to all Client Components via root-level AuthProvider

## Task Commits

> Note: Changes uncommitted — will be committed in phase transition commit.

| Task | Status | Description |
|------|--------|-------------|
| Task 1: lib/auth.tsx | PASS | AuthContext, AuthProvider, useAuth — dual-store login/logout |
| Task 2: layout.tsx + proxy.ts | PASS | AuthProvider in root layout, proxy.ts with matcher |
| Task 3: login + register forms | PASS | Client Component forms calling api.login/api.register |
| Checkpoint: human-verify | Approved | All 5 tests passed |

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/lib/auth.tsx` | Created | AuthContext, AuthProvider, useAuth hook |
| `frontend/proxy.ts` | Created | Route guard — redirects to /login if auth_token cookie absent |
| `frontend/app/layout.tsx` | Modified | Wrapped children with AuthProvider |
| `frontend/app/(auth)/login/page.tsx` | Modified | Working login form (Client Component) |
| `frontend/app/(auth)/register/page.tsx` | Modified | Working register form (Client Component) |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| proxy.ts not middleware.ts | Next.js 16 renamed the file; using deprecated name would break in future builds | All future Next.js 16 route guard references use proxy.ts |
| Dual-store (localStorage + cookie) | `apiFetch` needs Bearer token from localStorage; proxy.ts can only read cookies (Edge Runtime, no window) | Both stores must be kept in sync; login() and logout() do this atomically |
| AuthProvider at root layout | Simplest placement — available to all pages; avoids duplicate providers per route group | Phase 3+ pages can call useAuth() without additional setup |

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `grep` path error with parens in shell (unquoted) | Used quoted paths in subsequent bash commands — not a code issue |

## Next Phase Readiness

**Ready:**
- Auth flow complete: register, login, logout available via `useAuth()`
- `lib/api.ts` Bearer token sourced from localStorage — works in all Client Components
- Route protection in place: /map and /game/* require auth_token cookie
- Phase 3 (World Map) can import `useAuth()` and call `api.getAirports()` directly

**Concerns:**
- `<a href>` used in login/register nav links — causes full reload; swap to `<Link>` when UI is styled
- Token has no expiry check client-side — expired JWT will fail at the API call, not proactively

**Blockers:**
- None

---
*Phase: 02-nextjs-frontend-scaffold, Plan: 02*
*Completed: 2026-05-06*
