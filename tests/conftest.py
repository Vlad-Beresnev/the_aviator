import pytest
import sys
import os

# Add project root to path so modules are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def db_connection():
    """Live DB connection for integration tests. Skip if .env not present."""
    if not os.path.exists('.env'):
        pytest.skip("No .env file found — skipping DB integration tests")
    try:
        import config
        import mysql.connector
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        import db_manager
        db_manager.run_migrations()
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"DB connection failed: {e}")

@pytest.fixture
def cleanup_test_game(db_connection):
    """Delete test game rows created during tests."""
    yield
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM game WHERE name LIKE 'TEST_%'")
    db_connection.commit()
    cursor.close()
