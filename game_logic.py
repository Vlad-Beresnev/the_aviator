import airport_service
import player_service
import db_manager
import config


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _check_win() -> dict | None:
    """
    Return a win dict if all level airports have been beaten, else None.
    """
    level_airports = airport_service.get_level_airports()
    total = len(level_airports)
    beaten = sum(1 for a in level_airports if a["beaten"])
    if total > 0 and beaten >= total:
        return {"won": True, "win_type": "all_levels"}
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def new_game(player_name: str) -> dict:
    """Initialize a new game session for player_name."""
    return player_service.create_player_game(player_name)


def load_game(player_name: str) -> dict | None:
    """Load an existing game session for player_name."""
    return player_service.load_player_game(player_name)


def deliver_lecture(game_state: dict, airport_ident: str) -> dict:
    """
    Award the player for beating a level at airport_ident.

    - Rejects if the airport has already been beaten (LECT-04)
    - Adds speaker_fee to money (LECT-01)
    - Increments global_awareness by 1 (LECT-02)
    - Marks airport as is_unlocked=1 in DB (LECT-03)
    - Returns updated game_state dict on success, or {'error': str} on failure
    """
    if db_manager.is_airport_unlocked(airport_ident):
        return {"error": f"You have already beaten level at {airport_ident}."}

    goal = db_manager.get_goal(airport_ident)
    speaker_fee = goal["speaker_fee"] if goal else 0

    new_money = game_state["money"] + speaker_fee
    new_awareness = game_state["global_awareness"] + 1

    db_manager.deliver_lecture_transaction(game_state["id"], airport_ident, new_money, new_awareness)

    updated_state = {
        **game_state,
        "money": new_money,
        "global_awareness": new_awareness,
    }

    win = _check_win()
    if win:
        return {**updated_state, **win}

    return updated_state


def recharge(game_state: dict) -> dict:
    """
    Reload battery to full for a flat cost of RELOAD_COST.

    Returns updated game_state dict on success, or {'error': str} on failure.
    """
    if game_state["battery_used"] == 0:
        return {"error": "Battery is already full."}

    if game_state["money"] < config.RELOAD_COST:
        return {
            "error": (
                f"Not enough money. Reload costs ${config.RELOAD_COST:,} "
                f"but you only have ${game_state['money']:,}."
            )
        }

    new_money = game_state["money"] - config.RELOAD_COST
    new_battery_used = 0

    db_manager.update_after_recharge(game_state["id"], new_money, new_battery_used)

    return {
        **game_state,
        "money": new_money,
        "battery_used": new_battery_used,
    }
