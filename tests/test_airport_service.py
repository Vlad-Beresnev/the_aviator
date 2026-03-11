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
    """First level is always unlocked."""
    import airport_service
    result = airport_service.get_level_airports()
    assert result[0]["locked"] is False, "Level 1 should not be locked"


def test_get_level_airports_rest_locked(db_connection):
    """Sequential unlock: a level is locked if its predecessor is not beaten."""
    import airport_service
    result = airport_service.get_level_airports()
    for i, lv in enumerate(result):
        if i == 0:
            assert lv["locked"] is False, "Level 1 must always be unlocked"
        else:
            prev_beaten = result[i - 1]["beaten"]
            if not prev_beaten:
                assert lv["locked"] is True, (
                    f"Level {lv['level']} should be locked "
                    f"(level {result[i-1]['level']} not beaten)"
                )
