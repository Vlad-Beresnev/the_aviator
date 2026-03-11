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
    Return the airport record for a given ident as a plain dict, or None if not found.
    """
    return db_manager.get_airport(ident)


def get_level_airports() -> list:
    """
    Return all large airports as level entries sorted by difficulty ascending.

    First INITIAL_LEVELS airports are playable immediately.
    The rest are locked until all initial levels are beaten.

    Each item:
        {
            "ident": str,
            "name": str,
            "city": str,
            "speaker_fee": int,
            "difficulty": int,
            "continent": str,
            "beaten": bool,      # True if is_unlocked=1
            "locked": bool,      # True if beyond initial levels and not yet unlocked
            "level": int,        # 1-based level number
        }
    """
    all_airports = db_manager.get_all_large_airports()
    goals = db_manager.get_all_goals()

    levels = []
    for ap in all_airports:
        goal = goals.get(ap["ident"], {})
        levels.append({
            "ident": ap["ident"],
            "name": ap["name"],
            "city": ap["municipality"],
            "speaker_fee": goal.get("speaker_fee", 0),
            "difficulty": goal.get("difficulty", 1),
            "continent": ap["continent"],
            "beaten": bool(ap.get("is_unlocked", 0)),
        })

    # Sort by difficulty ascending, then by name for deterministic order
    levels.sort(key=lambda x: (x["difficulty"], x["name"] or ""))

    # Assign progressive difficulty (1-5 stars across 10 levels)
    # Levels 1-2: 1★, 3-4: 2★, 5-6: 3★, 7-8: 4★, 9-10: 5★
    # Beyond 10: repeat pattern
    for i, lv in enumerate(levels):
        lv["level"] = i + 1
        lv["difficulty"] = min(5, (i // 2) + 1)

    # Sequential unlock: level N+1 opens only after level N is beaten
    for i, lv in enumerate(levels):
        if i == 0:
            lv["locked"] = False  # First level always open
        else:
            lv["locked"] = not levels[i - 1]["beaten"]

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
