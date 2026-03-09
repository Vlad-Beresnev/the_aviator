# Requirements: The Aviator

**Defined:** 2026-03-09
**Core Value:** The player can navigate a global airport network, manage battery/money constraints, and progressively unlock airports through lectures — creating a satisfying loop of exploration and sustainable influence.

## v1 Requirements

### Game Setup

- [ ] **SETUP-01**: Player can start a new game by entering their name
- [ ] **SETUP-02**: New game is initialized in the database with default values (money=5000, battery=1000, global_awareness=0)
- [ ] **SETUP-03**: Player is placed at a random starting airport on new game
- [ ] **SETUP-04**: Player can continue an existing game session (load latest game record)
- [ ] **SETUP-05**: Player can quit the game from the main menu

### Navigation

- [ ] **NAV-01**: System calculates distance between two airports using the Haversine formula
- [ ] **NAV-02**: Player can view a list of reachable airports (within current battery range) with name, city, distance, battery cost, speaker fee, and difficulty level
- [ ] **NAV-03**: Player can fly to a selected reachable airport (battery deducted, location updated, persisted to DB)
- [ ] **NAV-04**: Flight is rejected with a message if the destination exceeds current battery range

### Battery Management

- [ ] **BATT-01**: Battery depletes during flight at rate of distance × 0.1 units/km (max capacity: 1000 units)
- [ ] **BATT-02**: Player can recharge battery at any airport (pays money proportional to units charged)
- [ ] **BATT-03**: Forced landing occurs if battery reaches zero mid-selection — player is teleported to the nearest airport with a money penalty
- [ ] **BATT-04**: Recharge is rejected if player has insufficient money

### Lecture & Progression

- [ ] **LECT-01**: Player can deliver a lecture at the current airport, earning the speaker fee (added to money)
- [ ] **LECT-02**: Delivering a lecture increments global_awareness score
- [ ] **LECT-03**: Airport is marked as unlocked (is_unlocked=1) in the database after a lecture
- [ ] **LECT-04**: Player cannot deliver a second lecture at an already-unlocked airport

### Win & Loss Conditions

- [ ] **WIN-01**: Player wins by unlocking airports across at least 3 different continents
- [ ] **WIN-02**: Player wins by accumulating $1,000,000 in money
- [ ] **WIN-03**: Win condition is checked after every action (fly, lecture, recharge)
- [ ] **WIN-04**: Player is shown a win screen with narrative text when win condition is met

### Status & Feedback

- [ ] **UI-01**: Player sees current status after every action: location, battery level, money, global_awareness, and number of airports unlocked
- [ ] **UI-02**: Invalid menu input prompts re-entry without crashing
- [ ] **UI-03**: Forced landing event displays a descriptive message before showing new location
- [ ] **UI-04**: All DB queries complete in under 1 second (performance requirement)

### Database & Persistence

- [ ] **DB-01**: Schema migrations applied: game table has money, global_awareness, battery_used columns; airport table has is_unlocked column
- [ ] **DB-02**: All game state persists in MariaDB — no in-memory-only state
- [ ] **DB-03**: Multi-step state updates (fly action: battery + location + unlock) are wrapped in a single transaction
- [x] **DB-04**: Database credentials loaded from .env file — never hardcoded in source code

### Code Architecture

- [ ] **ARCH-01**: Services return plain Python dicts/lists only — no class instances or mutable objects
- [x] **ARCH-02**: All SQL is contained in db_manager.py — no SQL strings in service or logic layers
- [ ] **ARCH-03**: No print() calls outside main.py — services and game_logic return data only
- [x] **ARCH-04**: Module structure matches assignment: config.py, db_manager.py, airport_service.py, player_service.py, game_logic.py, main.py

## v2 Requirements

### Web Interface

- **WEB-01**: Flask API routes wrap game_logic.py functions — same service layer, no changes
- **WEB-02**: Services return JSON-serializable dicts (guaranteed by v1 ARCH-01)
- **WEB-03**: Web frontend displays game state and accepts player input

### Enhanced Gameplay

- **GAME-01**: Difficulty level affects speaker fee payout formula
- **GAME-02**: Multiple narrative endings based on win path (continent spread vs. money)
- **GAME-03**: Continue/load screen shows previous game stats before resuming

## Out of Scope

| Feature | Reason |
|---------|--------|
| CO2 tracking as player metric | Contradicts sustainable development narrative; replaced by battery_used + global_awareness |
| Real-time flight animation | Brittle across terminals, adds no gameplay value |
| ASCII map rendering | Fragile across terminal widths, out of scope for coursework |
| Multiplayer / leaderboard | Single-player assignment |
| Multiple aircraft / upgrade trees | Scope creep; one plane for the entire game |
| Random weather / mechanical events | Undermines strategic battery planning |
| Mobile app | Web-first; mobile not planned |
| OAuth / user accounts | Single local player, no auth needed |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Pending |
| SETUP-02 | Phase 1 | Pending |
| SETUP-03 | Phase 1 | Pending |
| SETUP-04 | Phase 1 | Pending |
| SETUP-05 | Phase 4 | Pending |
| NAV-01 | Phase 2 | Pending |
| NAV-02 | Phase 2 | Pending |
| NAV-03 | Phase 2 | Pending |
| NAV-04 | Phase 2 | Pending |
| BATT-01 | Phase 2 | Pending |
| BATT-02 | Phase 2 | Pending |
| BATT-03 | Phase 3 | Pending |
| BATT-04 | Phase 2 | Pending |
| LECT-01 | Phase 2 | Pending |
| LECT-02 | Phase 2 | Pending |
| LECT-03 | Phase 2 | Pending |
| LECT-04 | Phase 2 | Pending |
| WIN-01 | Phase 3 | Pending |
| WIN-02 | Phase 3 | Pending |
| WIN-03 | Phase 3 | Pending |
| WIN-04 | Phase 4 | Pending |
| UI-01 | Phase 4 | Pending |
| UI-02 | Phase 4 | Pending |
| UI-03 | Phase 4 | Pending |
| UI-04 | Phase 2 | Pending |
| DB-01 | Phase 1 | Pending |
| DB-02 | Phase 1 | Pending |
| DB-03 | Phase 3 | Pending |
| DB-04 | Phase 1 | Complete |
| ARCH-01 | Phase 2 | Pending |
| ARCH-02 | Phase 1 | Complete |
| ARCH-03 | Phase 2 | Pending |
| ARCH-04 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after roadmap creation*
