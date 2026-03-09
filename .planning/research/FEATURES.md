# Feature Research

**Domain:** Python CLI strategy/educational game with database persistence
**Researched:** 2026-03-09
**Confidence:** MEDIUM — based on training knowledge of CLI game conventions, text-adventure UX patterns, and educational game design principles. No live search available; findings cross-referenced against project documents.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features that a player assumes are present. Missing any of these makes the game feel broken or unfinished.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Named player / new game setup | Every persistent game starts with identity; without it the game feels like a demo | LOW | `INSERT INTO game (player_name, ...)` on first run |
| Persistent game state across sessions | "Persistent" is in the spec; losing progress on exit destroys trust | MEDIUM | MariaDB via `mysql-connector-python`; save on every action, not just on quit |
| Current status display after every action | Player needs spatial / resource awareness at all times; missing = disorientation | LOW | Print location, battery %, money, global_awareness, airports unlocked after each turn |
| List of reachable airports with costs | Choosing where to fly without knowing the cost is a broken UX — not a puzzle, just friction | MEDIUM | Haversine filter: only show airports within current battery range; display name, fee, difficulty |
| Fly to a chosen airport | Core interaction — without it there is no game | MEDIUM | Validate choice is in the reachable list; deduct battery; persist location |
| Battery resource constraint | Player expects a meaningful resource to manage — it is the central mechanic | LOW | `battery_used += distance * 0.1`; cap at 1000 units |
| Recharge at airport | Resource constraint is only meaningful if recovery is possible | LOW | Cost proportional to units charged; deduct money; persist |
| Lecture / unlock action at destination | The reward loop; without it flying has no purpose | LOW | Increment global_awareness, add speaker_fee to money, set is_unlocked = 1 |
| Graceful handling of invalid input | CLI games break badly on bad input; re-prompting is baseline UX | LOW | Wrap `input()` in a validation loop; never crash on bad data |
| Win condition feedback | Player needs to know when they've won — otherwise the game has no end | LOW | Check continent spread or $1M threshold after each turn; print clear victory message |
| Forced landing on battery empty (not game-over) | Hard resets are frustrating in exploration games; players expect consequences, not termination | LOW | Teleport to nearest airport, apply money penalty, persist state |

### Differentiators (Competitive Advantage)

Features that make The Aviator distinct from a generic "fly between airports" CLI exercise.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Global awareness score as the win metric | Frames aviation as a force for good rather than just wealth accumulation; aligns with the sustainable-development narrative | LOW | Simple integer counter; already in schema; differentiates from generic resource grind |
| Difficulty level per airport (corporate resistance) | Adds strategic texture — high-fee/high-difficulty airports create risk/reward decisions | LOW | Already encoded in `goal.target_maxvalue`; display it; can adjust fee payout formula |
| Continent-spread win condition | Forces player to think globally, not just grind the nearest cluster of airports | LOW | Query `airport.continent` (or derive from lat/lon bucket); check ≥ N distinct continents unlocked |
| Narrative framing (oil corporations as antagonists) | Gives emotional stakes to mechanical choices; players care about decisions when there's a story | LOW | Text strings only — no extra code; triggered at game start, forced landing, and win screen |
| Forced landing flavor text | Turns a penalty event into a story beat; reinforces the "underdog vs corporations" narrative | LOW | Random choice from a list of landing messages; single `random.choice()` call |
| Battery as an ecological metaphor | Battery use = energy budget; recharging = resource stewardship; makes the sustainability theme mechanical, not cosmetic | LOW | The mechanic already exists; the framing is what differentiates it |
| Phase 2 readiness (service layer returns dicts) | The CLI is a thin presentation layer; the real value is the service layer that becomes a JSON API | MEDIUM | Controller-Service-Repository enforced from day one; no mixed-layer logic |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Save / load menu with named slots | Players are used to this from desktop games | Adds UI complexity with no real benefit — state is always persisted in the DB automatically; "resume" is the only needed flow | Auto-persist on every action; on startup, detect existing game and offer "continue or new game" |
| CO2 tracking as a player metric | Seems thematically obvious for a sustainability game | Penalizes the player for the core action (flying); creates a contradictory loop where winning = more CO2 | Use battery_used (energy management) + global_awareness (positive impact score) instead |
| Real-time / animated flight sequence | Adds visual flair in a terminal | Requires `time.sleep()` loops and ANSI escape codes; breaks non-TTY environments; slows CI/testing; adds no gameplay value | Single descriptive print line: "Flying 847 km to Oslo... Battery: 84 → 0 units" |
| Leaderboard / high scores | Competitive element feels natural for a scoring game | This is single-player coursework; adding a leaderboard requires user accounts, network calls, or shared DB — out of scope and fragile | Win screen shows personal best; comparison to own previous runs is enough |
| Random events (weather, mechanical failures) | Makes the game feel less predictable | Introduces uncontrollable outcomes that undermine strategic planning; bad for educational demonstration | Use deterministic difficulty levels per airport as the variable challenge |
| Map rendering in terminal | Visually satisfying, shows spatial context | Complex ASCII map rendering is brittle across terminal widths; libraries like `curses` add significant complexity | Show lat/lon coordinates and cardinal direction hint ("NE, 847 km") in the airport list |
| Multiple aircraft / upgrades | Progression system feels rewarding | Phase 1 scope is the core loop; upgrades require inventory system, another DB table, UI branching; defer entirely | Progression is expressed through airport unlocks and global_awareness growth |

---

## Feature Dependencies

```
[New Game Setup]
    └──requires──> [DB Connection + Schema]
                       └──requires──> [config.py + db_manager.py]

[Fly to Airport]
    └──requires──> [List Reachable Airports]
                       └──requires──> [Haversine Distance Calculator]
                                          └──requires──> [Airport coordinates in DB]
    └──requires──> [Battery Resource State]
                       └──requires──> [Persistent Game State]

[Lecture / Unlock Action]
    └──requires──> [Fly to Airport] (must have arrived)
    └──requires──> [Persistent Game State] (to write is_unlocked, update money/global_awareness)

[Recharge Battery]
    └──requires──> [Persistent Game State]
    └──requires──> [Money Resource State]

[Forced Landing]
    └──requires──> [Haversine Distance Calculator] (to find nearest airport)
    └──requires──> [Persistent Game State] (to teleport + deduct penalty)

[Win Condition Check]
    └──requires──> [Lecture / Unlock Action] (unlocks feed the check)
    └──enhances──> [Status Display] (win is shown after status)

[Status Display] ──enhances──> [Every Action] (shown after every state change)

[Continent-Spread Win] ──conflicts with──> [Simple Airport-Count Win]
    (choose one primary condition; both can be checked but one should be "primary" to avoid confusing the player)
```

### Dependency Notes

- **Fly to Airport requires Haversine Distance Calculator:** The reachable airport list cannot be generated without geodesic distance; this is a blocking prerequisite.
- **Lecture requires Fly to Airport:** You can only lecture at your current location; the action makes no sense before arrival is established.
- **Forced Landing requires Haversine:** Finding the nearest airport for emergency landing uses the same distance function as navigation.
- **All game actions require Persistent Game State:** Every mutation (battery, money, global_awareness, location, is_unlocked) must be written to the DB in the same request that changes it; deferred batch saves risk state corruption.
- **Status Display enhances every action:** It is not a separate feature but a contract — every action ends with a status print. Implement it as a single `display_status(player)` function called after every state change.

---

## MVP Definition

### Launch With (v1 — Phase 1 CLI)

- [ ] New game setup with player name, random starting airport — establishes identity and initial state
- [ ] Haversine distance calculator — gates all navigation features
- [ ] List reachable airports with battery cost, speaker fee, difficulty — the core decision surface
- [ ] Fly to chosen airport (battery deduction, location update, persist) — the core action
- [ ] Lecture at current airport (global_awareness + money, mark is_unlocked) — the core reward
- [ ] Recharge battery at airport (money cost, battery restore, persist) — resource recovery
- [ ] Forced landing on battery empty (teleport to nearest, money penalty) — consequence system
- [ ] Status display after every action (location, battery, money, global_awareness, airports unlocked) — player orientation
- [ ] Win condition check after each action (continent spread or $1M) — game end
- [ ] Invalid input re-prompting — basic stability

### Add After Validation (v1.x)

- [ ] Continue vs new game prompt on startup — once persistence is proven, resuming a session becomes important
- [ ] Narrative flavor text (forced landing messages, win screen story beat) — adds emotional resonance with minimal code

### Future Consideration (v2+)

- [ ] Web interface (Phase 2) — explicitly out of scope for Phase 1; service layer is already designed to support this
- [ ] Difficulty scaling (corporate resistance affects fee payout formula) — interesting mechanic but adds balancing complexity
- [ ] Multiple win paths with different narrative endings — valuable for replayability; deferred until core loop is validated

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| New game setup + DB init | HIGH | LOW | P1 |
| Haversine distance calculator | HIGH | LOW | P1 |
| List reachable airports | HIGH | LOW | P1 |
| Fly to airport (with persistence) | HIGH | LOW | P1 |
| Lecture / unlock action | HIGH | LOW | P1 |
| Status display after every action | HIGH | LOW | P1 |
| Recharge battery | HIGH | LOW | P1 |
| Forced landing (battery empty) | HIGH | LOW | P1 |
| Win condition check | HIGH | LOW | P1 |
| Invalid input handling | HIGH | LOW | P1 |
| Continue vs new game on startup | MEDIUM | LOW | P2 |
| Narrative flavor text | MEDIUM | LOW | P2 |
| Continent-spread win condition detail | MEDIUM | LOW | P2 |
| Difficulty level affecting payout | MEDIUM | MEDIUM | P3 |
| Real-time flight animation | LOW | MEDIUM | — (anti-feature) |
| ASCII map rendering | LOW | HIGH | — (anti-feature) |
| Multiple aircraft / upgrades | LOW | HIGH | — (anti-feature) |

**Priority key:**
- P1: Must have for Phase 1 launch
- P2: Add once core loop is working and validated
- P3: Consider only if time permits after P2

---

## Competitor Feature Analysis

The closest analogues are: Python coursework airport games (common in Finnish AMK curricula), Zork/Inform-style text adventures, and Geography quiz games with CLI.

| Feature | Typical AMK Airport Game | Classic Text Adventure (Zork-style) | The Aviator Approach |
|---------|--------------------------|--------------------------------------|----------------------|
| Persistent state | File-based JSON or no persistence | No persistence (load from file) | MariaDB — enables Phase 2 upgrade |
| Resource management | Single resource (fuel) | Inventory count | Two resources (battery + money) with interplay |
| Win condition | Reach destination | Escape dungeon | Multi-continent unlock OR wealth threshold |
| Failure state | Game over on empty fuel | Game over on death | Forced landing penalty — keeps game flowing |
| Educational content | None | None | Sustainability narrative woven into mechanics |
| Architecture | Flat script | Flat script | Controller-Service-Repository — Phase 2 ready |

---

## Sources

- Project documents: `.planning/PROJECT.md`, `high-level-plan.md`, `Määrittelydokumentin_pohja.md` — HIGH confidence
- Training knowledge of Python CLI game conventions and text-adventure UX patterns (Zork, Inform 7, Python coursework patterns) — MEDIUM confidence (well-established conventions, unlikely to have changed)
- Educational game design principles (feedback loops, consequence vs game-over, resource constraints as metaphor) — MEDIUM confidence (grounded in game design literature through August 2025)
- Note: WebSearch and Brave Search unavailable at research time; no live verification performed

---

*Feature research for: Python CLI educational strategy game with MariaDB persistence*
*Researched: 2026-03-09*
