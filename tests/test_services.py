"""Тесты вспомогательных функций."""

import pytest

from src.aeroplane import Aeroplane
from src.services import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    parse_altitude_range,
    sort_aeroplanes,
)


def _planes() -> list[Aeroplane]:
    return [
        Aeroplane("A", "Spain", 200.0, 5000.0),
        Aeroplane("B", "Germany", 250.0, 12000.0),
        Aeroplane("C", "Spain", 180.0, 9000.0),
        Aeroplane("D", "United States", 300.0, 15000.0),
    ]


def test_filter_aeroplanes_by_country():
    result = filter_aeroplanes(_planes(), ["Spain"])
    assert len(result) == 2
    assert all("Spain" in p.origin_country for p in result)


def test_filter_empty_countries_returns_all():
    assert filter_aeroplanes(_planes(), []) == _planes()


def test_parse_altitude_range():
    assert parse_altitude_range("1000 - 5000") == (1000.0, 5000.0)
    assert parse_altitude_range("5000-1000") == (1000.0, 5000.0)


def test_parse_altitude_range_invalid():
    with pytest.raises(ValueError):
        parse_altitude_range("invalid")


def test_get_aeroplanes_by_altitude():
    result = get_aeroplanes_by_altitude(_planes(), "8000 - 13000")
    assert len(result) == 2
    assert all(8000 <= p.baro_altitude <= 13000 for p in result)


def test_sort_aeroplanes_descending():
    sorted_planes = sort_aeroplanes(_planes(), by="baro_altitude", descending=True)
    altitudes = [p.baro_altitude for p in sorted_planes]
    assert altitudes == sorted(altitudes, reverse=True)


def test_get_top_aeroplanes():
    top = get_top_aeroplanes(_planes(), 2)
    assert len(top) == 2
    assert top[0].baro_altitude >= top[1].baro_altitude


def test_get_top_invalid_n():
    with pytest.raises(ValueError):
        get_top_aeroplanes(_planes(), 0)
