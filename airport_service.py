import math
import db_manager
import config


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Return great-circle distance in kilometres between two lat/lon points.

    Uses the Haversine formula with Earth radius R = 6371 km.
    """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_airport(ident: str) -> dict | None:
    """
    Return the playable level entry for a large airport ident, or the raw airport
    record for non-level airports. Returns None if not found.
    """
    for airport in get_level_airports():
        if airport["ident"] == ident:
            return airport

    return db_manager.get_airport(ident)


def get_level_airports() -> list:
    """
    Return all large airports as level entries sorted by difficulty ascending.

    All level airports are playable immediately. Beaten state is still tracked
    separately so rewards, completion, and win checks keep working.

    Each item:
        {
            "ident": str,
            "name": str,
            "city": str,
            "speaker_fee": int,
            "difficulty": int,
            "continent": str,
            "beaten": bool,      # True if is_unlocked=1
            "locked": bool,      # Always False; no level-gating restrictions
            "level": int,        # 1-based level number
        }
    """
    return _build_level_airports(db_manager.get_all_large_airports())


def get_level_airports_in_bounds(
    south: float,
    north: float,
    west: float,
    east: float,
) -> list:
    """Return playable large airports inside the requested map viewport."""
    airports = db_manager.get_large_airports_in_bounds(south, north, west, east)
    return _build_level_airports(airports)


def _build_level_airports(airports: list) -> list:
    goals = db_manager.get_all_goals()

    levels = []
    for ap in airports:
        goal = goals.get(ap["ident"], {})
        levels.append({
            "ident": ap["ident"],
            "name": ap["name"],
            "city": ap["municipality"],
            "latitude_deg": ap["latitude_deg"],
            "longitude_deg": ap["longitude_deg"],
            "speaker_fee": goal.get("speaker_fee", 0),
            "difficulty": goal.get("difficulty", 1),
            "continent": ap["continent"],
            "beaten": bool(ap.get("is_unlocked", 0)),
        })

    levels.sort(key=lambda x: (x["difficulty"], x["name"] or ""))

    for i, lv in enumerate(levels):
        lv["level"] = i + 1
        lv["locked"] = False

    return levels


def get_reachable_airports(current_airport_ident: str, battery_remaining: float) -> list:
    """
    Return a list of large airports reachable from current_airport_ident within battery_remaining.
    Kept for backward compatibility / game-over checks.
    """
    current = db_manager.get_airport(current_airport_ident)
    if current is None:
        return []

    all_airports = db_manager.get_all_large_airports()
    goals = db_manager.get_all_goals()

    reachable = []
    for ap in all_airports:
        if ap["ident"] == current_airport_ident:
            continue
        dist = _haversine(
            current["latitude_deg"], current["longitude_deg"],
            ap["latitude_deg"], ap["longitude_deg"]
        )
        battery_cost = round(dist * 0.1, 4)
        if battery_cost > battery_remaining:
            continue
        goal = goals.get(ap["ident"], {})
        reachable.append({
            "ident": ap["ident"],
            "name": ap["name"],
            "city": ap["municipality"],
            "distance_km": round(dist, 2),
            "battery_cost": battery_cost,
            "speaker_fee": goal.get("speaker_fee", 0),
            "difficulty": goal.get("difficulty", None),
            "continent": ap["continent"],
        })

    return reachable
