# ✈ The Aviator

A CLI + Pygame hybrid game where you pilot the world's first electric aircraft around the globe, delivering lectures on sustainable aviation to unlock new destinations.

**Beat all levels to prove electric flight can conquer the skies!**

## Gameplay

- **Navigate** between real-world airports (7 000+ in the database)
- **Survive** top-down arcade levels — dodge and shoot enemy planes
- **Manage** your battery (fuel) and money across flights
- **Progress** through increasingly difficult levels with scaling enemy AI

### Controls (action level)

| Key | Action |
|-----|--------|
| `← → ↑ ↓` / `W A S D` | Move plane |
| `Space` | Fire (also auto-fires) |
| `Esc` | Abort level |

### Controls (CLI menus)

Navigate with **↑ ↓ arrows** and **Enter**, or type a number directly.

## Prerequisites

- **Python 3.12+**
- **MySQL or MariaDB** server (local or remote)

## Installation

```bash
# Clone the repo
git clone https://github.com/vlad-beresnev/the_aviator.git
cd the_aviator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Database Setup

1. **Create a MySQL/MariaDB database** for the project.

2. **Copy and fill in your credentials:**

   ```bash
   cp .env.example .env
   # Edit .env with your DB_USER, DB_PASSWORD, DB_NAME, DB_HOST
   ```

3. **Initialize the database** (loads airport data + creates game tables):

   ```bash
   python scripts/init_db.py
   ```

   This imports ~7 000 airports from `db/lp_project_base.sql` and runs the game's migrations automatically.

## Running the Game

```bash
python main.py
```

## Running Tests

```bash
python -m pytest tests/ -q
```

## Project Structure

```
main.py                CLI entry point — menus, game loop
action_game.py         Pygame 2D survival-shooter (action levels)
sprites.py             Programmatic pixel-art sprite generator
game_logic.py          Core game mechanics (new game, lectures, recharge)
airport_service.py     Airport queries, Haversine distance, level system
player_service.py      Player persistence helpers
db_manager.py          Database layer — all SQL, connections, migrations
config.py              Configuration (from .env) and game constants
scripts/init_db.py     One-time database initializer
db/
  lp_project_base.sql  Airport schema + data (~7 000 airports)
tests/                 47 tests (unit, integration, security, architecture)
```

### Architecture

The project follows a **Repository → Service → UI** pattern:

| Layer | Files | Responsibility |
|-------|-------|----------------|
| Repository | `db_manager.py` | All SQL queries, parameterized statements |
| Service | `game_logic.py`, `airport_service.py`, `player_service.py` | Pure logic, returns dicts |
| UI | `main.py` | Terminal interface (Rich) |
| Game | `action_game.py`, `sprites.py` | Pygame action levels |

## Configuration

All settings are in `config.py`. Key values:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_BATTERY` | 1000 | Maximum fuel capacity |
| `STARTING_MONEY` | 5000 | Initial money |
| `LEVEL_DURATION` | 75s | Time to survive per level |
| `GAME_WIDTH × GAME_HEIGHT` | 1024 × 768 | Game window size |

## Database Schema

The project uses 4 tables. Full dump: `db/aviator_dev_dump.sql`

### `airport` (7 000+ rows — imported from `db/lp_project_base.sql`)

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| `id` | INT | | Numeric ID |
| `ident` | VARCHAR(40) | **PK** | ICAO code (e.g. `EFHK`) |
| `type` | VARCHAR(40) | | `large_airport`, `medium_airport`, etc. |
| `name` | VARCHAR(40) | | Airport name |
| `latitude_deg` | DOUBLE | | GPS latitude |
| `longitude_deg` | DOUBLE | | GPS longitude |
| `elevation_ft` | INT | | Elevation in feet |
| `continent` | VARCHAR(40) | | Continent code |
| `iso_country` | VARCHAR(40) | | Country ISO code |
| `iso_region` | VARCHAR(40) | | Region code |
| `municipality` | VARCHAR(40) | | City name |
| `scheduled_service` | VARCHAR(40) | | `yes` / `no` |
| `gps_code` | VARCHAR(40) | | GPS code |
| `iata_code` | VARCHAR(40) | | IATA code (e.g. `HEL`) |
| `local_code` | VARCHAR(40) | | Local code |
| `home_link` | VARCHAR(40) | | Website URL |
| `wikipedia_link` | VARCHAR(40) | | Wikipedia URL |
| `keywords` | VARCHAR(40) | | Search keywords |
| `is_unlocked` | TINYINT(1) | | `0`/`1` — unlocked by beating a level |

### `country`

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| `iso_country` | VARCHAR(40) | **PK** | Country ISO code |
| `name` | VARCHAR(40) | | Country name |
| `continent` | VARCHAR(40) | | Continent code |
| `wikipedia_link` | VARCHAR(40) | | Wikipedia URL |
| `keywords` | VARCHAR(40) | | Search keywords |

### `game`

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| `id` | INT | **PK** (auto) | Game save ID |
| `name` | VARCHAR(100) | | Player name |
| `money` | INT | | Current money (default 5000) |
| `battery_used` | DOUBLE | | Fuel consumed so far |
| `global_awareness` | INT | | Score counter |
| `current_airport` | VARCHAR(40) | **FK → airport.ident** | Player's current location |

### `goal`

| Column | Type | Key | Description |
|--------|------|-----|-------------|
| `id` | INT | **PK** (auto) | Goal ID |
| `airport_ident` | VARCHAR(40) | **FK → airport.ident**, UNIQUE | Target airport |
| `target_minvalue` | INT | | Speaker fee min |
| `target_maxvalue` | INT | | Speaker fee max |

### Foreign Keys

| From | Column | → To | Column |
|------|--------|------|--------|
| `game` | `current_airport` | `airport` | `ident` |
| `goal` | `airport_ident` | `airport` | `ident` |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)