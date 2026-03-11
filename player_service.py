import db_manager
import config


def create_player_game(player_name: str) -> dict:
    """
    Create a new game row for player_name at the starting airport (config.STARTING_AIRPORT).

    Returns the new game record as a plain dict:
        {id, name, money, battery_used, global_awareness, current_airport}
    """
    return db_manager.create_game(player_name, config.STARTING_AIRPORT)


def load_player_game(player_name: str) -> dict | None:
    """
    Load the most recent game record for player_name.

    Returns game dict or None if no game found for this name.
    """
    return db_manager.get_latest_game(player_name)
