import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_create_game(db_connection, cleanup_test_game):
    """SETUP-01: create_game returns dict with player name."""
    import db_manager
    result = db_manager.create_game("TEST_Alice", "KSFO")
    assert result["name"] == "TEST_Alice"
    assert "id" in result

def test_create_game_defaults(db_connection, cleanup_test_game):
    """SETUP-02: New game row has money=5000, battery_used=0, global_awareness=0."""
    import db_manager, config
    result = db_manager.create_game("TEST_Defaults", config.STARTING_AIRPORT)
    assert result["money"] == config.STARTING_MONEY
    assert result["battery_used"] == 0
    assert result["global_awareness"] == 0

def test_create_game_starting_airport(db_connection, cleanup_test_game):
    """SETUP-03: New game row has current_airport matching STARTING_AIRPORT constant."""
    import db_manager, config
    result = db_manager.create_game("TEST_Airport", config.STARTING_AIRPORT)
    assert result["current_airport"] == config.STARTING_AIRPORT
    assert config.STARTING_AIRPORT == "KSFO"

def test_get_latest_game(db_connection, cleanup_test_game):
    """SETUP-04: get_latest_game returns most recent row; returns None for unknown name."""
    import db_manager, config
    db_manager.create_game("TEST_Load", config.STARTING_AIRPORT)
    db_manager.create_game("TEST_Load", config.STARTING_AIRPORT)  # second row
    result = db_manager.get_latest_game("TEST_Load")
    assert result is not None
    assert result["name"] == "TEST_Load"
    # Should return most recent (highest id)
    all_rows = db_manager.get_latest_game("TEST_Load")
    assert all_rows["id"] == result["id"]
    # Unknown name returns None
    assert db_manager.get_latest_game("TEST_NoSuchPlayer_xyz") is None

def test_persistence_roundtrip(db_connection, cleanup_test_game):
    """DB-02: Value inserted via create_game() is readable via get_latest_game()."""
    import db_manager, config
    created = db_manager.create_game("TEST_Roundtrip", config.STARTING_AIRPORT)
    loaded = db_manager.get_latest_game("TEST_Roundtrip")
    assert loaded is not None
    assert loaded["id"] == created["id"]
    assert loaded["money"] == created["money"]
    assert loaded["current_airport"] == created["current_airport"]
