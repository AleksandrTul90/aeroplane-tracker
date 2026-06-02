"""Тесты JSONSaver."""

import json
from pathlib import Path

import pytest

from src.aeroplane import Aeroplane
from src.json_saver import JSONSaver
from src.services import filter_aeroplanes


@pytest.fixture
def temp_storage(tmp_path: Path) -> JSONSaver:
    return JSONSaver(file_path=tmp_path / "planes.json")


def _sample_plane(callsign: str = "UAL1", country: str = "United States") -> Aeroplane:
    return Aeroplane(callsign, country, 250.0, 10000.0, icao24="abc111")


def test_load_aeroplanes_from_file_returns_objects(temp_storage: JSONSaver):
    plane = _sample_plane()
    temp_storage.add_aeroplane(plane)
    planes = temp_storage.load_aeroplanes_from_file()
    assert len(planes) == 1
    assert isinstance(planes[0], Aeroplane)
    assert planes[0].callsign == "UAL1"


def test_add_and_get_aeroplane(temp_storage: JSONSaver):
    plane = _sample_plane()
    temp_storage.add_aeroplane(plane)
    planes = temp_storage.get_aeroplanes()
    assert len(planes) == 1
    assert planes[0].callsign == "UAL1"


def test_add_updates_duplicate(temp_storage: JSONSaver):
    plane = _sample_plane()
    temp_storage.add_aeroplane(plane)
    updated = Aeroplane("UAL1", "United States", 300.0, 12000.0, icao24="abc111")
    temp_storage.add_aeroplane(updated)
    planes = temp_storage.load_aeroplanes_from_file()
    assert len(planes) == 1
    assert planes[0].velocity == 300.0
    assert planes[0].baro_altitude == 12000.0


def test_filter_by_country_via_services(temp_storage: JSONSaver):
    temp_storage.add_aeroplane(_sample_plane("A1", "Spain"))
    temp_storage.add_aeroplane(
        Aeroplane("A2", "Germany", 250.0, 10000.0, icao24="def222")
    )
    all_planes = temp_storage.load_aeroplanes_from_file()
    spain_planes = filter_aeroplanes(all_planes, ["Spain"])
    assert len(spain_planes) == 1
    assert spain_planes[0].origin_country == "Spain"


def test_delete_by_callsign(temp_storage: JSONSaver):
    temp_storage.add_aeroplane(_sample_plane("DEL1", "France"))
    assert temp_storage.delete_aeroplane_by_callsign("DEL1") is True
    assert temp_storage.load_aeroplanes_from_file() == []


def test_delete_nonexistent(temp_storage: JSONSaver):
    assert temp_storage.delete_aeroplane_by_callsign("NOPE") is False


def test_delete_empty_callsign_raises(temp_storage: JSONSaver):
    with pytest.raises(ValueError):
        temp_storage.delete_aeroplane_by_callsign("  ")


def test_invalid_json_raises(tmp_path: Path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{not json", encoding="utf-8")
    saver = JSONSaver(file_path=bad_file)
    with pytest.raises(ValueError, match="некорректный JSON"):
        saver.load_aeroplanes_from_file()


def test_json_file_format(temp_storage: JSONSaver, tmp_path: Path):
    temp_storage.add_aeroplane(_sample_plane())
    raw = json.loads((tmp_path / "planes.json").read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    assert raw[0]["callsign"] == "UAL1"
