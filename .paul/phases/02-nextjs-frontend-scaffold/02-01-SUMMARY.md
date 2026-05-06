---
phase: 02-nextjs-frontend-scaffold
plan: 01
subsystem: ui
tags: [nextjs, typescript, tailwind, app-router, cors, fetch, api-client]

requires:
  - phase: 01-fastapi-api-layer
    provides: All 8 API endpoints with JWT auth — typed in lib/api.ts

provides:
  - Next.js 16 app scaffold (TypeScript, Tailwind, App Router)
  - 5 stub pages at correct routes + root redirect
  - lib/api.ts typed fetch wrapper for all Phase 1 endpoints
  - CORS on FastAPI allowing localhost:3000
affects: [02-02-auth-context, 03-world-map, 04-browser-game, 05-leaderboard]

tech-stack:
  added: [next@16.2.4, react@19, typescript, tailwind@4, eslint-config-next]
  patterns: [App Router route groups, async params (Next.js 16), internal apiFetch helper]

key-files:
  created: [frontend/lib/api.ts, frontend/app/(auth)/login/page.tsx, frontend/app/(auth)/register/page.tsx, frontend/app/(game)/map/page.tsx, frontend/app/(game)/game/[ident]/page.tsx, frontend/app/(game)/leaderboard/page.tsx]
  modified: [api/main.py, frontend/app/page.tsx, frontend/.env.local]

key-decisions:
  - "Next.js 16 async params: params in dynamic routes is Promise<{...}> — must be awaited"
  - "apiFetch is kept internal: all callers use api.* exports, never apiFetch directly"

patterns-established:
  - "Route groups: (auth)/ and (game)/ group routes without affecting URLs"
  - "API client pattern: single lib/api.ts, internal apiFetch<T> generic, named api.* exports"

duration: ~15min
started: 2026-05-06T00:00:00Z
completed: 2026-05-06T00:00:00Z
---

# Phase 2 Plan 01: Next.js Frontend Scaffold Summary

**Next.js 16 app scaffolded with App Router route groups, 5 stub pages, typed API client for all 8 Phase 1 endpoints, and CORS on FastAPI — build passes with 0 TypeScript errors.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15 min |
| Started | 2026-05-06 |
| Completed | 2026-05-06 |
| Tasks | 3 completed |
| Files modified | 10 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: App runs and all 5 routes render | Pass | All 6 page.tsx files exist; build confirms routes compiled |
| AC-2: TypeScript compiles without errors | Pass | `bun run build` exits 0, Turbopack reports 0 errors |
| AC-3: CORS allows frontend origin | Pass | CORSMiddleware configured for http://localhost:3000 |

## Accomplishments

- Scaffolded Next.js 16 with TypeScript, Tailwind v4, App Router — 351 packages, build in ~2s
- Created route groups `(auth)/` and `(game)/` — 5 stub pages at correct URLs, root redirects to `/login`
- `lib/api.ts` wraps all 8 Phase 1 endpoints with TypeScript generics — single source of truth for all API calls

## Task Commits

> Note: No atomic commits per task were made during this APPLY — changes went directly to working tree. Commit to be made during phase transition.

| Task | Status | Description |
|------|--------|-------------|
| Task 1: Scaffold + CORS | PASS | Created frontend/, .env.local, added CORSMiddleware to api/main.py |
| Task 2: Route groups + stubs | PASS | 6 page.tsx files at correct paths |
| Task 3: lib/api.ts | PASS | 4 interfaces, 8 typed API functions |

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `frontend/` | Created (scaffold) | Next.js 16 app — TypeScript, Tailwind, App Router |
| `frontend/.env.local` | Created | NEXT_PUBLIC_API_URL=http://localhost:8000 |
| `frontend/app/page.tsx` | Modified | Replaced boilerplate — redirects to /login |
| `frontend/app/(auth)/login/page.tsx` | Created | Stub page at /login |
| `frontend/app/(auth)/register/page.tsx` | Created | Stub page at /register |
| `frontend/app/(game)/map/page.tsx` | Created | Stub page at /map |
| `frontend/app/(game)/game/[ident]/page.tsx` | Created | Dynamic stub at /game/[ident], async params |
| `frontend/app/(game)/leaderboard/page.tsx` | Created | Stub page at /leaderboard |
| `frontend/lib/api.ts` | Created | Typed fetch wrapper for all 8 Phase 1 endpoints |
| `api/main.py` | Modified | CORSMiddleware added for localhost:3000 |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Next.js 16 async params | Installed version was 16.2.4, not 14 as planned. `params` is `Promise<{...}>` in v15+. Used `async/await` per official docs. | All dynamic pages must use async function + `await params`. Plan 02-02 must follow same pattern. |
| Route groups `(auth)/` + `(game)/` | Follows plan spec — organizes pages by concern without affecting URLs | Allows per-group layouts in future plans |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential: corrected params API for Next.js 16 |
| Scope additions | 0 | None |
| Deferred | 0 | None |

**Total impact:** One essential fix for version mismatch — no scope creep, plan goal fully met.

### Auto-fixed Issues

**1. Next.js version mismatch — async params**
- **Found during:** Task 2 (route stubs)
- **Issue:** Plan specified `{ params }: { params: { ident: string } }` (Next.js 14 sync pattern); installed version is 16.2.4 where params is `Promise<{ ident: string }>`
- **Fix:** Made `GamePage` async, added `const { ident } = await params;` per Next.js 16 `page.md` docs
- **Files:** `frontend/app/(game)/game/[ident]/page.tsx`
- **Verification:** `bun run build` passed with 0 TypeScript errors

## Next Phase Readiness

**Ready:**
- Route structure is in place — all pages at correct URLs
- `lib/api.ts` exports typed wrappers for all 8 endpoints — ready to call from components
- CORS configured — browser fetch from localhost:3000 → localhost:8000 will work
- `frontend/.env.local` present — API URL available via `process.env.NEXT_PUBLIC_API_URL`

**Concerns:**
- `localStorage` token reads in `apiFetch` will silently return `null` during SSR (server has no `window`). Guarded with `typeof window !== 'undefined'` — pages calling API must be Client Components or use Server Actions. Plan 02-02 auth context must account for this.
- `frontend/app/layout.tsx` still has Next.js default boilerplate (Geist fonts, metadata). Fine for now.

**Blockers:**
- None

---
*Phase: 02-nextjs-frontend-scaffold, Plan: 01*
*Completed: 2026-05-06*
