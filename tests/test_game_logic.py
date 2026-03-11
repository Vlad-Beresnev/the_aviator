import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# new_game / load_game
# ---------------------------------------------------------------------------

def test_new_game_returns_dict(db_connection, cleanup_test_game):
    """new_game returns a dict with game state keys."""
    import game_logic
    result = game_logic.new_game("TEST_GlNew")
    assert isinstance(result, dict)
    for key in ("id", "name", "money", "battery_used", "global_awareness", "current_airport"):
        assert key in result


def test_new_game_starting_location(db_connection, cleanup_test_game):
    """new_game places player at STARTING_AIRPORT."""
    import game_logic, config
    result = game_logic.new_game("TEST_GlStart")
    assert result["current_airport"] == config.STARTING_AIRPORT


def test_load_game_returns_dict(db_connection, cleanup_test_game):
    """load_game returns the saved game state."""
    import game_logic
    created = game_logic.new_game("TEST_GlLoad")
    loaded = game_logic.load_game("TEST_GlLoad")
    assert loaded is not None
    assert loaded["id"] == created["id"]


def test_load_game_none_for_unknown(db_connection):
    """load_game returns None when no game exists for the player."""
    import game_logic
    result = game_logic.load_game("TEST_GlNoSuchPlayer_xyz")
    assert result is None


# ---------------------------------------------------------------------------
# deliver_lecture — now takes airport_ident parameter
# ---------------------------------------------------------------------------

def test_deliver_lecture_adds_speaker_fee(db_connection, cleanup_test_game):
    """LECT-01: deliver_lecture adds speaker_fee to money."""
    import game_logic, db_manager
    state = game_logic.new_game("TEST_GlLect")
    money_before = state["money"]
    goal = db_manager.get_goal("KLAX")
    result = game_logic.deliver_lecture(state, "KLAX")
    assert "error" not in result
    assert result["money"] == money_before + goal["speaker_fee"]


def test_deliver_lecture_increments_awareness(db_connection, cleanup_test_game):
    """LECT-02: deliver_lecture increments global_awareness by 1."""
    import game_logic
    state = game_logic.new_game("TEST_GlAware")
    awareness_before = state["global_awareness"]
    result = game_logic.deliver_lecture(state, "KLAX")
    assert "error" not in result
    assert result["global_awareness"] == awareness_before + 1


def test_deliver_lecture_marks_airport_unlocked(db_connection, cleanup_test_game):
    """LECT-03: deliver_lecture sets is_unlocked=1 for the airport in DB."""
    import game_logic, db_manager
    state = game_logic.new_game("TEST_GlUnlock")
    game_logic.deliver_lecture(state, "KLAX")
    assert db_manager.is_airport_unlocked("KLAX") is True


def test_deliver_lecture_prevents_duplicate(db_connection, cleanup_test_game):
    """LECT-04: second deliver_lecture at same airport returns error."""
    import game_logic
    state = game_logic.new_game("TEST_GlDup")
    game_logic.deliver_lecture(state, "KLAX")
    # Try again — should fail
    state2 = game_logic.load_game("TEST_GlDup")
    result = game_logic.deliver_lecture(state2, "KLAX")
    assert "error" in result


def test_deliver_lecture_persists(db_connection, cleanup_test_game):
    """LECT-01/02: lecture changes persist when game is reloaded."""
    import game_logic, db_manager
    state = game_logic.new_game("TEST_GlPersist")
    goal = db_manager.get_goal("KLAX")
    after_lecture = game_logic.deliver_lecture(state, "KLAX")
    assert "error" not in after_lecture
    loaded = game_logic.load_game("TEST_GlPersist")
    assert loaded["money"] == state["money"] + goal["speaker_fee"]


# ---------------------------------------------------------------------------
# Win condition: all levels beaten
# ---------------------------------------------------------------------------

def test_win_condition_triggers(db_connection, cleanup_test_game):
    """WIN: _check_win returns won dict when all levels are beaten."""
    import game_logic
    from unittest.mock import patch
    fake_levels = [
        {"ident": "KLAX", "beaten": True, "locked": False, "level": 1},
        {"ident": "KJFK", "beaten": True, "locked": False, "level": 2},
    ]
    with patch("airport_service.get_level_airports", return_value=fake_levels):
        result = game_logic._check_win()
    assert result is not None
    assert result["won"] is True
    assert result["win_type"] == "all_levels"


def test_no_win_when_levels_remain(db_connection, cleanup_test_game):
    """WIN: _check_win returns None when not all levels are beaten."""
    import game_logic
    from unittest.mock import patch
    fake_levels = [
        {"ident": "KLAX", "beaten": True, "locked": False, "level": 1},
        {"ident": "KJFK", "beaten": False, "locked": False, "level": 2},
    ]
    with patch("airport_service.get_level_airports", return_value=fake_levels):
        result = game_logic._check_win()
    assert result is None


# ---------------------------------------------------------------------------
# recharge — now flat cost, no units parameter
# ---------------------------------------------------------------------------

def test_recharge_flat_cost(db_connection, cleanup_test_game):
    """RELOAD: recharge deducts RELOAD_COST and sets battery_used to 0."""
    import game_logic, config, db_manager
    state = game_logic.new_game("TEST_GlReload")
    # Simulate some battery usage
    db_manager.update_after_recharge(state["id"], state["money"], 500)
    state["battery_used"] = 500
    result = game_logic.recharge(state)
    assert "error" not in result
    assert result["money"] == state["money"] - config.RELOAD_COST
    assert result["battery_used"] == 0


def test_recharge_rejects_full_battery(db_connection, cleanup_test_game):
    """RELOAD: recharge returns error when battery is already full."""
    import game_logic
    state = game_logic.new_game("TEST_GlRechFull")
    result = game_logic.recharge(state)
    assert "error" in result


def test_recharge_rejects_insufficient_money(db_connection, cleanup_test_game):
    """RELOAD: recharge returns error when money < RELOAD_COST."""
    import game_logic, db_manager
    state = game_logic.new_game("TEST_GlRechPoor")
    db_manager.update_after_recharge(state["id"], 0, 500)
    state["battery_used"] = 500
    state["money"] = 0
    result = game_logic.recharge(state)
    assert "error" in result


def test_recharge_persists(db_connection, cleanup_test_game):
    """RELOAD: recharge changes persist when game is reloaded."""
    import game_logic, db_manager
    state = game_logic.new_game("TEST_GlRechSave")
    db_manager.update_after_recharge(state["id"], state["money"], 500)
    state["battery_used"] = 500
    result = game_logic.recharge(state)
    assert "error" not in result
    loaded = game_logic.load_game("TEST_GlRechSave")
    assert loaded["money"] == result["money"]
    assert loaded["battery_used"] == 0
