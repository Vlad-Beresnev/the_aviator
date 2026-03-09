import os
import glob

def test_no_hardcoded_credentials():
    """DB-04: No password string literal in any .py file (excludes .env, db/populatedb.py)."""
    py_files = glob.glob("**/*.py", recursive=True)
    # Exclude the populate script (run-once manual script, not updated in Phase 1)
    excluded = {"db/populatedb.py", os.path.join("db", "populatedb.py")}
    violations = []
    for path in py_files:
        norm = os.path.normpath(path)
        if norm in {os.path.normpath(e) for e in excluded}:
            continue
        with open(path) as f:
            for i, line in enumerate(f, 1):
                lower = line.lower()
                # Flag lines with password= followed by a quoted non-empty value
                if "password=" in lower and ("password=os" not in lower) and ("password=none" not in lower):
                    # Allow password=config.DB_PASSWORD and password=os.getenv(...) patterns
                    if "os.getenv" not in line and "config." not in line and "#" not in line.split("password=")[0]:
                        violations.append(f"{path}:{i}: {line.rstrip()}")
    assert not violations, f"Hardcoded password found:\n" + "\n".join(violations)
