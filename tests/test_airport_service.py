import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Unit tests (no DB needed)
# ---------------------------------------------------------------------------

def test_haversine_ksfo_klax():
    """NAV-01: Haversine distance KSFO→KLAX is approximately 543 km (±10 km tolerance)."""
    import airport_service
    # KSFO: 37.6189, -122.3750  |  KLAX: 33.9425, -118.4081
    dist = airport_service._haversine(37.6189, -122.3750, 33.9425, -118.4081)
    assert 533 <= dist <= 553, f"Expected ~543 km, got {dist:.1f} km"


def test_haversine_same_airport():
    """Haversine of same point is 0."""
    import airport_service
    dist = airport_service._haversine(37.6189, -122.3750, 37.6189, -122.3750)
    assert dist == pytest.approx(0.0, abs=0.01)


def test_level_airports_are_all_playable_without_db(monkeypatch):
    """Level availability does not depend on previous beaten levels."""
    import airport_service

    monkeypatch.setattr(airport_service.db_manager, "get_all_large_airports", lambda: [
        {
            "ident": "AAA",
            "name": "Airport A",
            "municipality": "City A",
            "latitude_deg": 1.0,
            "longitude_deg": 1.0,
            "continent": "EU",
            "is_unlocked": 0,
        },
        {
            "ident": "BBB",
            "name": "Airport B",
            "municipality": "City B",
            "latitude_deg": 2.0,
            "longitude_deg": 2.0,
            "continent": "EU",
            "is_unlocked": 0,
        },
    ])
    monkeypatch.setattr(airport_service.db_manager, "get_all_goals", lambda: {
        "AAA": {"speaker_fee": 1000, "difficulty": 1},
        "BBB": {"speaker_fee": 2000, "difficulty": 2},
    })

    levels = airport_service.get_level_airports()

    assert [level["locked"] for level in levels] == [False, False]


def test_level_airports_preserve_goal_difficulty_without_db(monkeypatch):
    """Difficulty comes from goal data, not the airport's level index."""
    import airport_service

    monkeypatch.setattr(airport_service.db_manager, "get_all_large_airports", lambda: [
        {
            "ident": f"AP{i}",
            "name": f"Airport {i}",
            "municipality": f"City {i}",
            "latitude_deg": float(i),
            "longitude_deg": float(i),
            "continent": "EU",
            "is_unlocked": 0,
        }
        for i in range(1, 7)
    ])
    monkeypatch.setattr(airport_service.db_manager, "get_all_goals", lambda: {
        "AP1": {"speaker_fee": 1000, "difficulty": 5},
        "AP2": {"speaker_fee": 1000, "difficulty": 1},
        "AP3": {"speaker_fee": 1000, "difficulty": 4},
        "AP4": {"speaker_fee": 1000, "difficulty": 2},
        "AP5": {"speaker_fee": 1000, "difficulty": 3},
        "AP6": {"speaker_fee": 1000, "difficulty": 5},
    })

    levels = airport_service.get_level_airports()

    assert [level["difficulty"] for level in levels] == [1, 2, 3, 4, 5, 5]


def test_level_airports_in_bounds_uses_viewport_query_without_db(monkeypatch):
    """Viewport level loading uses the bounded airport query instead of all airports."""
    import airport_service

    captured_bounds = {}

    def fake_airports_in_bounds(south, north, west, east):
        captured_bounds.update({"south": south, "north": north, "west": west, "east": east})
        return [
            {
                "ident": "AAA",
                "name": "Airport A",
                "municipality": "City A",
                "latitude_deg": 1.0,
                "longitude_deg": 1.0,
                "continent": "EU",
                "is_unlocked": 0,
            },
        ]

    monkeypatch.setattr(airport_service.db_manager, "get_large_airports_in_bounds", fake_airports_in_bounds)
    monkeypatch.setattr(airport_service.db_manager, "get_all_goals", lambda: {
        "AAA": {"speaker_fee": 1000, "difficulty": 1},
    })

    levels = airport_service.get_level_airports_in_bounds(-10, 10, 170, -170)

    assert captured_bounds == {"south": -10, "north": 10, "west": 170, "east": -170}
    assert [level["ident"] for level in levels] == ["AAA"]


def test_get_airport_returns_level_shape_without_db(monkeypatch):
    """Large airport lookups return the playable API shape used by the web game."""
    import airport_service

    level_airport = {
        "ident": "AAA",
        "name": "Airport A",
        "city": "City A",
        "latitude_deg": 1.0,
        "longitude_deg": 1.0,
        "continent": "EU",
        "beaten": False,
        "locked": False,
        "level": 1,
        "difficulty": 1,
        "speaker_fee": 1000,
    }

    monkeypatch.setattr(airport_service, "get_level_airports", lambda: [level_airport])

    assert airport_service.get_airport("AAA") == level_airport


# ---------------------------------------------------------------------------
# Integration tests (require DB)
# ---------------------------------------------------------------------------

def test_get_airport_ksfo(db_connection):
    """get_airport returns a dict with expected keys for a known ident."""
    import airport_service
    airport = airport_service.get_airport("KSFO")
    assert airport is not None
    assert airport["ident"] == "KSFO"
    assert "name" in airport
    assert "latitude_deg" in airport
    assert "longitude_deg" in airport
    assert "continent" in airport


def test_get_airport_unknown(db_connection):
    """get_airport returns None for an unknown ident."""
    import airport_service
    result = airport_service.get_airport("ZZZUNKNOWN")
    assert result is None


def test_get_reachable_airports_returns_list(db_connection):
    """NAV-02: get_reachable_airports returns a list."""
    import airport_service
    result = airport_service.get_reachable_airports("KSFO", 1000)
    assert isinstance(result, list)


def test_get_reachable_airports_fields(db_connection):
    """NAV-02: Each reachable airport has all required fields."""
    import airport_service
    result = airport_service.get_reachable_airports("KSFO", 1000)
    assert len(result) > 0, "Expected at least one reachable airport from KSFO with full battery"
    for ap in result[:5]:  # check first 5
        for field in ("ident", "name", "city", "distance_km", "battery_cost", "speaker_fee", "difficulty", "continent"):
            assert field in ap, f"Missing field '{field}' in airport dict"


def test_get_reachable_airports_large_only(db_connection):
    """NAV-02: Only large airports are returned (type = 'large_airport')."""
    import airport_service, db_manager
    result = airport_service.get_reachable_airports("KSFO", 1000)
    # Spot-check: fetch raw DB data for returned idents and verify type
    if result:
        sample_idents = [r["ident"] for r in result[:10]]
        conn = db_manager._get_connection()
        cursor = conn.cursor(dictionary=True)
        placeholders = ",".join(["%s"] * len(sample_idents))
        cursor.execute(
            f"SELECT ident, type FROM airport WHERE ident IN ({placeholders})",
            sample_idents
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        for row in rows:
            assert row["type"] == "large_airport", (
                f"Expected large_airport but got '{row['type']}' for {row['ident']}"
            )


def test_get_reachable_airports_excludes_current(db_connection):
    """Current airport is not included in reachable list."""
    import airport_service
    result = airport_service.get_reachable_airports("KSFO", 1000)
    idents = [r["ident"] for r in result]
    assert "KSFO" not in idents


def test_get_reachable_airports_battery_filter(db_connection):
    """NAV-04: Airports with battery_cost > battery_remaining are excluded."""
    import airport_service
    # With battery=1 (0.1 * distance → only airports within 10 km), virtually none reachable
    result = airport_service.get_reachable_airports("KSFO", 1)
    for ap in result:
        assert ap["battery_cost"] <= 1, (
            f"Airport {ap['ident']} has battery_cost {ap['battery_cost']} but battery was 1"
        )


def test_get_reachable_airports_battery_cost_formula(db_connection):
    """BATT-01: battery_cost equals distance_km * 0.1."""
    import airport_service
    result = airport_service.get_reachable_airports("KSFO", 1000)
    for ap in result[:10]:
        expected = ap["distance_km"] * 0.1
        assert ap["battery_cost"] == pytest.approx(expected, rel=1e-5)


# ---------------------------------------------------------------------------
# get_level_airports (new level system)
# ---------------------------------------------------------------------------

def test_get_level_airports_returns_list(db_connection):
    """get_level_airports returns a non-empty list of level dicts."""
    import airport_service
    result = airport_service.get_level_airports()
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_level_airports_fields(db_connection):
    """Each level entry has required fields."""
    import airport_service
    result = airport_service.get_level_airports()
    for lv in result[:5]:
        for field in ("ident", "name", "city", "speaker_fee", "difficulty", "continent", "beaten", "locked", "level"):
            assert field in lv, f"Missing field '{field}' in level dict"


def test_get_level_airports_sorted_by_difficulty(db_connection):
    """Levels are sorted by difficulty ascending."""
    import airport_service
    result = airport_service.get_level_airports()
    difficulties = [lv["difficulty"] for lv in result]
    assert difficulties == sorted(difficulties)


def test_get_level_airports_initial_unlocked(db_connection):
    """First level is playable."""
    import airport_service
    result = airport_service.get_level_airports()
    assert result[0]["locked"] is False, "Level 1 should not be locked"


def test_get_level_airports_all_playable(db_connection):
    """All level airports are playable regardless of completion order."""
    import airport_service
    result = airport_service.get_level_airports()
    assert all(lv["locked"] is False for lv in result)
