import os
from dotenv import load_dotenv

load_dotenv()  # reads .env from working directory

DB_HOST = os.getenv("DB_HOST", "mysql.metropolia.fi")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Fail fast if credentials are missing — better error than cryptic mysql failure
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise EnvironmentError(
        "Missing required DB credentials. "
        "Copy .env.example to .env and fill in DB_USER, DB_PASSWORD, DB_NAME."
    )

# Game constants
STARTING_AIRPORT = "KSFO"   # San Francisco International — fixed starting location
MAX_BATTERY = 1000
STARTING_MONEY = 5000
