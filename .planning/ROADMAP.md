# Roadmap: The Aviator

## Overview

The Aviator is built bottom-up along its dependency graph: the database and configuration layer comes first because every other layer rests on it. The service layer (airport navigation, player state) comes next because the game controller cannot be written until services return correct data. The controller and win condition logic follow, completing the core gameplay loop. Finally, the CLI presentation layer wires all outputs into a playable terminal experience. This order prevents the most dangerous pitfalls — architectural drift, SQL leaking into services, and untestable integration — by making clean layer boundaries a structural constraint, not a discipline.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Database schema, credentials, and module skeleton are in place
- [ ] **Phase 2: Service Layer** - Airport navigation and player state services deliver the core game loop actions
- [ ] **Phase 3: Game Controller** - Controller orchestrates services into game rules, win conditions, and forced landing
- [ ] **Phase 4: CLI and Polish** - Terminal game loop, status display, input validation, and win screen complete the playable game

## Phase Details

### Phase 1: Foundation
**Goal**: The database schema is correct, credentials are safe, and the module skeleton enforces layer boundaries before any game logic is written
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04, DB-01, DB-02, DB-04, ARCH-02, ARCH-04
**Success Criteria** (what must be TRUE):
  1. Running `python main.py` connects to MariaDB without error and the game table has money, global_awareness, battery_used, and is_unlocked columns
  2. A new game row is inserted with default values (money=5000, battery=1000, global_awareness=0) when a player provides their name
  3. An existing game session loads by reading the latest game record from the database — no duplicate rows are created
  4. Database credentials are read from a .env file; no passwords appear in any source file or git history
  5. All SQL strings exist only in db_manager.py; main.py, airport_service.py, player_service.py, and game_logic.py contain no SQL
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Environment setup: .gitignore, .env.example, test scaffold (pytest + 4 test files)
- [ ] 01-02-PLAN.md — Core implementation: config.py (credentials + constants) and db_manager.py (migrations + CRUD)
- [ ] 01-03-PLAN.md — Module stubs: airport_service.py, player_service.py, game_logic.py, main.py with correct import chains

### Phase 2: Service Layer
**Goal**: Airport navigation and player state services are complete, returning plain dicts, and the core actions — view airports, fly, lecture, recharge — work end-to-end with persistence
**Depends on**: Phase 1
**Requirements**: NAV-01, NAV-02, NAV-03, NAV-04, BATT-01, BATT-02, BATT-04, LECT-01, LECT-02, LECT-03, LECT-04, UI-04, ARCH-01, ARCH-03
**Success Criteria** (what must be TRUE):
  1. Player can view a list of reachable airports showing name, city, distance (km), battery cost, speaker fee, and difficulty — only airports within battery range appear
  2. Flying to an airport deducts the correct battery amount (distance × 0.1), updates the player's location in the database, and the change persists if the game is loaded again
  3. Delivering a lecture at an airport adds the speaker fee to money, increments global_awareness by 1, and marks the airport as is_unlocked=1; the same airport cannot be lectured at twice
  4. Recharging battery adds battery units and deducts money proportionally; a recharge attempt with insufficient money is rejected with a message
  5. All database queries return within 1 second during normal play
**Plans**: TBD

### Phase 3: Game Controller
**Goal**: game_logic.py orchestrates services into complete game actions with transaction safety, forced landing recovery, and win condition evaluation after every action
**Depends on**: Phase 2
**Requirements**: BATT-03, WIN-01, WIN-02, WIN-03, DB-03
**Success Criteria** (what must be TRUE):
  1. If battery reaches zero, the player is immediately teleported to the nearest airport and a money penalty is applied — game continues from the new location
  2. After every fly, lecture, or recharge action, the game checks whether the player has unlocked airports on at least 3 continents or has $1,000,000 — and stops the game if either condition is met
  3. A flight action (battery deduction + location update + optional unlock) executes as a single database transaction — a simulated failure mid-action leaves no partial state
**Plans**: TBD

### Phase 4: CLI and Polish
**Goal**: main.py delivers a complete playable terminal experience — startup menu, status display, numbered selection, input validation, forced landing feedback, and win screen
**Depends on**: Phase 3
**Requirements**: SETUP-05, WIN-04, UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. On launch, the player sees a menu to start a new game, continue an existing game, or quit — selecting quit exits cleanly
  2. After every action, the player sees their current location, battery level, money, global_awareness score, and number of airports unlocked
  3. Entering invalid menu input (letters where numbers expected, out-of-range selections) re-prompts without crashing or printing a stack trace
  4. Forced landing displays a descriptive narrative message before showing the new location and updated status
  5. Reaching a win condition displays a narrative win screen before exiting
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/3 | Not started | - |
| 2. Service Layer | 0/TBD | Not started | - |
| 3. Game Controller | 0/TBD | Not started | - |
| 4. CLI and Polish | 0/TBD | Not started | - |
