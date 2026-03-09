import db_manager


def get_reachable_airports(current_airport_ident: str, battery_remaining: float) -> list:
    """
    Return a list of airports reachable from current_airport_ident within battery_remaining.

    Each item in the list is a plain dict:
        {
            "ident": str,
            "name": str,
            "city": str,          # municipality column in airport table
            "distance_km": float,
            "battery_cost": float, # distance_km * 0.1
            "speaker_fee": int,
            "difficulty": str,
            "continent": str,
        }

    Uses Haversine formula for distance calculation (implemented in Phase 2).
    Only airports with battery_cost <= battery_remaining are included.
    Implemented in Phase 2.
    """
    pass


def get_airport(ident: str) -> dict | None:
    """
    Return the airport record for a given ident as a plain dict, or None if not found.

    Implemented in Phase 2.
    """
    pass
