# The Aviator

## What This Is

The Aviator is a Python-based strategy game where the player takes the role of a visionary inventor piloting the world's first fully electric long-range private aircraft. The player flies between airports around the world, delivers sustainability lectures to "unlock" each airport, manages battery and money resources, and fights against oil corporations to spread clean aviation. Phase 1 is a CLI game; Phase 2 upgrades it to a web interface.

## Core Value

The player can navigate a global airport network, manage battery/money constraints, and progressively unlock airports through lectures — creating a satisfying loop of exploration and sustainable influence.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Player can start a new game with a name, placed at a random starting airport
- [ ] Player can view available nearby airports with speaker fee and difficulty level
- [ ] Player can fly to a reachable airport (within battery range using Haversine distance)
- [ ] Battery depletes during flight (distance × 0.1 units/km, max 1000 units)
- [ ] Player can recharge battery at any airport (costs money proportional to units charged)
- [ ] Player can deliver a lecture at destination, earning speaker fee and incrementing global_awareness
- [ ] Visited airport is marked as unlocked (is_unlocked = 1) in the database
- [ ] Forced landing occurs if battery hits zero — player teleported to nearest airport with money penalty
- [ ] Player wins by unlocking airports across multiple continents or accumulating $1,000,000
- [ ] Player sees current status (location, battery, money, global_awareness, progress) after every action
- [ ] Invalid input is handled gracefully with re-prompt
- [ ] Game state persists in MariaDB/MySQL via Controller-Service-Repository architecture

### Out of Scope

- Web/API interface — Phase 2 only
- CO2 tracking as a player metric — replaced by battery_used and global_awareness
- Mobile app — not planned
- Multiplayer — single-player game

## Context

- **Existing asset**: An airport database (MariaDB/MySQL) already exists with airport coordinates (lat/lon), which the game queries for navigation.
- **Schema changes needed**: `game` table needs `money`, `global_awareness` columns and rename `co2_consumed` → `battery_used`; `goal` table stores speaker_fee (target_minvalue) and difficulty_level (target_maxvalue); `airport` table needs `is_unlocked` boolean column.
- **Assignment context**: Metropolia AMK coursework — Ohjelmisto 1 ja 2. Phase 1 deadline is the CLI version; Phase 2 is the web version.
- **Architecture decision**: Controller-Service-Repository pattern from the start so Phase 2 backend is a drop-in upgrade — service layer returns Python dicts/lists (later JSON).

## Constraints

- **Tech stack**: Python with `mysql-connector-python`; MariaDB/MySQL database — already chosen and required by assignment
- **CLI first**: Phase 1 is terminal-only; no web framework until Phase 2
- **Performance**: Database queries must complete in < 1 second
- **Module structure**: Must follow the defined file layout: `config.py`, `db_manager.py`, `airport_service.py`, `player_service.py`, `game_logic.py`, `main.py`

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Haversine formula for distance | Standard geodesic formula for Earth distances between lat/lon points | — Pending |
| Battery model: distance × 0.1, max 1000 | Simple, predictable resource constraint that forces strategic routing | — Pending |
| Controller-Service-Repository pattern | Minimizes rework when upgrading to web in Phase 2 | — Pending |
| global_awareness as win metric (not CO2) | Aligns with sustainable development narrative; avoids penalizing the player for flying | — Pending |
| Forced landing on battery empty (not game over) | Keeps game flowing; adds penalty without frustration of hard restart | — Pending |

## External References

- **Finnish open data portal**: https://avoindata.suomi.fi/fi — national open data catalogue; potential source for additional aviation or geographic datasets
- **Metropolia assignment example**: https://github.com/ilkkamtk/software-1-project-example — reference implementation showing expected structure and scope for Ohjelmisto 1 coursework

---
*Last updated: 2026-03-09 after initialization*
