import db_manager


def create_player_game(player_name: str) -> dict:
    """
    Create a new game row for player_name at the starting airport (config.STARTING_AIRPORT).

    Returns the new game record as a plain dict:
        {id, name, money, battery_used, global_awareness, current_airport}

    Delegates to db_manager.create_game(). Implemented in Phase 2.
    """
    pass


def load_player_game(player_name: str) -> dict | None:
    """
    Load the most recent game record for player_name.

    Returns game dict or None if no game found for this name.
    Shows clear error message ("No game found for [name]") when None — handled in game_logic.
    Delegates to db_manager.get_latest_game(). Implemented in Phase 2.
    """
    pass
