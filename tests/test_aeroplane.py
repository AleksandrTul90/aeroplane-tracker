"""Тесты модели Aeroplane."""

import pytest

from src.aeroplane import Aeroplane


@pytest.fixture
def slow_plane() -> Aeroplane:
    return Aeroplane("SLOW01", "Spain", 100.0, 5000.0)


@pytest.fixture
def fast_plane() -> Aeroplane:
    return Aeroplane("FAST01", "Spain", 300.0, 5000.0)


@pytest.fixture
def low_plane() -> Aeroplane:
    return Aeroplane("LOW01", "Germany", 200.0, 1000.0)


@pytest.fixture
def high_plane() -> Aeroplane:
    return Aeroplane("HIGH01", "Germany", 200.0, 12000.0)


def test_aeroplane_creation_valid():
    plane = Aeroplane("UAL1621", "United States", 268.79, 10203.18)
    assert plane.callsign == "UAL1621"
    assert plane.origin_country == "United States"
    assert plane.velocity == 268.79
    assert plane.baro_altitude == 10203.18


def test_aeroplane_strips_callsign():
    plane = Aeroplane("  ABC123  ", "Germany", 100.0, 5000.0)
    assert plane.callsign == "ABC123"


def test_validation_empty_callsign():
    with pytest.raises(ValueError, match="Позывной"):
        Aeroplane("", "Spain", 100.0, 1000.0)


def test_validation_empty_country():
    with pytest.raises(ValueError, match="Страна"):
        Aeroplane("ABC", "", 100.0, 1000.0)


def test_validation_negative_velocity():
    with pytest.raises(ValueError, match="Скорость"):
        Aeroplane("ABC", "Spain", -1.0, 1000.0)


def test_compare_by_speed(slow_plane: Aeroplane, fast_plane: Aeroplane):
    """Метод экземпляра: self.compare_by_speed(other)."""
    result = slow_plane.compare_by_speed(fast_plane)
    assert result == -1

    result_fast = fast_plane.compare_by_speed(slow_plane)
    assert result_fast == 1

    same = slow_plane.compare_by_speed(slow_plane)
    assert same == 0


def test_compare_by_altitude(low_plane: Aeroplane, high_plane: Aeroplane):
    """Метод экземпляра: self.compare_by_altitude(other)."""
    result = low_plane.compare_by_altitude(high_plane)
    assert result == -1

    result_high = high_plane.compare_by_altitude(low_plane)
    assert result_high == 1


def test_is_faster_than(slow_plane: Aeroplane, fast_plane: Aeroplane):
    assert fast_plane.is_faster_than(slow_plane) is True
    assert slow_plane.is_faster_than(fast_plane) is False


def test_is_higher_than(low_plane: Aeroplane, high_plane: Aeroplane):
    assert high_plane.is_higher_than(low_plane) is True
    assert low_plane.is_higher_than(high_plane) is False


def test_compare_by_speed_invalid_other(slow_plane: Aeroplane):
    with pytest.raises(TypeError):
        slow_plane.compare_by_speed("not-a-plane")  # type: ignore[arg-type]


def test_compare_by_altitude_magic_methods(low_plane: Aeroplane, high_plane: Aeroplane):
    assert low_plane < high_plane
    assert high_plane > low_plane
    assert low_plane != high_plane
    assert not (low_plane == high_plane)


def test_from_opensky_state():
    state = [
        "abc123",
        "UAL1621 ",
        "United States",
        None,
        None,
        -75.0,
        40.0,
        10203.18,
        False,
        268.79,
    ]
    plane = Aeroplane.from_opensky_state(state)
    assert plane is not None
    assert plane.callsign == "UAL1621"
    assert plane.origin_country == "United States"
    assert plane.baro_altitude == 10203.18
    assert plane.velocity == 268.79


def test_cast_to_object_list_from_dict():
    payload = {
        "states": [
            ["id1", "AAA", "Spain", None, None, 0, 0, 1000, False, 200],
        ]
    }
    planes = Aeroplane.cast_to_object_list(payload)
    assert len(planes) == 1
    assert planes[0].callsign == "AAA"


def test_cast_to_object_list_skips_invalid():
    states = [
        ["id1", "AAA", "Spain", None, None, 0, 0, 1000, False, 200],
        None,
        ["id2", None, "France", None, None, 0, 0, None, False, None],
    ]
    planes = Aeroplane.cast_to_object_list(states)
    assert len(planes) == 2


def test_to_dict_and_from_dict():
    plane = Aeroplane("TEST", "Germany", 150.0, 8000.0, icao24="de123")
    data = plane.to_dict()
    restored = Aeroplane.from_dict(data)
    assert restored.callsign == plane.callsign
    assert restored.origin_country == plane.origin_country
    assert restored.velocity == plane.velocity
    assert restored.baro_altitude == plane.baro_altitude
