import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_create_player_game_returns_dict(db_connection, cleanup_test_game):
    """SETUP-01: create_player_game returns a dict with expected keys."""
    import player_service
    result = player_service.create_player_game("TEST_PsCreate")
    assert isinstance(result, dict)
    for key in ("id", "name", "money", "battery_used", "global_awareness", "current_airport"):
        assert key in result, f"Missing key '{key}' in result"


def test_create_player_game_defaults(db_connection, cleanup_test_game):
    """SETUP-02: create_player_game uses correct default values."""
    import player_service, config
    result = player_service.create_player_game("TEST_PsDefaults")
    assert result["money"] == config.STARTING_MONEY
    assert result["battery_used"] == 0
    assert result["global_awareness"] == 0
    assert result["current_airport"] == config.STARTING_AIRPORT


def test_load_player_game_returns_latest(db_connection, cleanup_test_game):
    """SETUP-04: load_player_game returns the most recent game record."""
    import player_service
    first = player_service.create_player_game("TEST_PsLoad")
    second = player_service.create_player_game("TEST_PsLoad")
    result = player_service.load_player_game("TEST_PsLoad")
    assert result is not None
    assert result["id"] == second["id"]  # most recent


def test_load_player_game_none_for_unknown(db_connection):
    """SETUP-04: load_player_game returns None for a player with no game."""
    import player_service
    result = player_service.load_player_game("TEST_PsNoSuchPlayer_xyz")
    assert result is None
