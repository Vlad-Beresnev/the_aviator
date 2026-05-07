import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from working directory

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")

# Game constants
STARTING_AIRPORT = "KSFO"   # San Francisco International — fixed starting location
MAX_BATTERY = 1000
STARTING_MONEY = 5000
RECHARGE_RATE = 1.0          # Cost in dollars per battery unit recharged
RELOAD_COST = 1000           # Flat cost to reload battery to max

# Action game (Pygame)
GAME_WIDTH = 1024
GAME_HEIGHT = 768
LEVEL_DURATION = 75          # Seconds to survive per level
FPS = 75

# Enemy scaling — base values (scale with level/difficulty)
ENEMY_BASE_SPEED = 1.45
ENEMY_BASE_SPAWN_INTERVAL = 100  # Frames between spawns at level 1
ENEMY_BASE_FIRE_INTERVAL = 150   # Frames between enemy shots at level 1
DIFFICULTY_SCALE_STEP = 0.18
LEVEL_SCALE_STEP = 0.025
MAX_LEVEL_SCALE_BONUS = 0.75
IN_LEVEL_RAMP_MAX = 0.35
PLAYER_SPEED = 8
PLAYER_FIRE_INTERVAL = 7         # Frames between player shots
BULLET_SPEED = 11
ENEMY_BULLET_SPEED = 4.5
HIT_DAMAGE = 40                  # Battery damage per enemy hit
