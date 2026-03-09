import airport_service
import player_service
import config


def new_game(player_name: str) -> dict:
    """
    Initialize a new game session for player_name.

    - Creates a game row via player_service.create_player_game()
    - Returns the initial game state dict

    Implemented in Phase 2.
    """
    pass


def load_game(player_name: str) -> dict | None:
    """
    Load an existing game session for player_name.

    - Loads game row via player_service.load_player_game()
    - Returns game state dict, or None if no game found

    Implemented in Phase 2.
    """
    pass
