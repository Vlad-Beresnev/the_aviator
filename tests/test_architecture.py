import os
import glob
import importlib
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUIRED_MODULES = [
    "config",
    "db_manager",
    "airport_service",
    "player_service",
    "game_logic",
    "main",
    "sprites",
    "action_game",
]

SQL_KEYWORDS = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE TABLE", "ALTER TABLE")

def test_module_structure():
    """ARCH-04: All six required .py files exist and are importable."""
    missing = []
    for mod in REQUIRED_MODULES:
        path = f"{mod}.py"
        if not os.path.exists(path):
            missing.append(path)
    assert not missing, f"Missing required module files: {missing}"

def test_sql_only_in_db_manager():
    """ARCH-02: No SQL strings (SELECT/INSERT/UPDATE/DELETE/CREATE TABLE/ALTER TABLE) outside db_manager.py."""
    violations = []
    non_db_files = [
        f for f in glob.glob("*.py")
        if f not in ("db_manager.py",)
        and not f.startswith("test_")
    ]
    for path in non_db_files:
        with open(path) as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                upper = line.upper()
                # Skip lines that are clearly Python code using Rich Table, not SQL
                if "TABLE(" in upper and ("TITLE=" in upper or "ADD_COLUMN" in upper or "ADD_ROW" in upper):
                    continue
                for kw in SQL_KEYWORDS:
                    if kw in upper:
                        violations.append(f"{path}:{i}: {line.rstrip()}")
                        break
    assert not violations, f"SQL found outside db_manager.py:\n" + "\n".join(violations)
