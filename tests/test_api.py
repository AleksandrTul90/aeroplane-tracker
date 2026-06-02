"""Тесты AeroplanesAPI."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.aeroplanes_api import APIAdapter, AeroplanesAPI


NOMINATIM_RESPONSE = [
    {
        "boundingbox": ["36.0", "44.0", "-9.5", "3.5"],
        "display_name": "Spain",
    }
]

OPENSKY_RESPONSE = {
    "states": [
        ["abc", "IBE123 ", "Spain", None, None, -3.0, 40.0, 9000, False, 220.0]
    ]
}


@patch("src.aeroplanes_api.get")
@patch("src.aeroplanes_api.requests.Session")
def test_get_aeroplanes_success(mock_session_cls, mock_get):
    session = MagicMock()
    mock_session_cls.return_value = session

    connect_resp = MagicMock()
    connect_resp.raise_for_status = MagicMock()

    nominatim_resp = MagicMock()
    nominatim_resp.raise_for_status = MagicMock()
    nominatim_resp.json.return_value = NOMINATIM_RESPONSE

    opensky_resp = MagicMock()
    opensky_resp.raise_for_status = MagicMock()
    opensky_resp.json.return_value = OPENSKY_RESPONSE

    session.get.return_value = connect_resp
    mock_get.side_effect = [nominatim_resp, opensky_resp]

    api = AeroplanesAPI()
    result = api.get_aeroplanes("Spain")

    assert len(result) == 1
    assert result[0][1].strip() == "IBE123"
    assert api.aeroplanes == OPENSKY_RESPONSE


def test_api_adapter_alias():
    assert APIAdapter is AeroplanesAPI


@patch("src.aeroplanes_api.get")
def test_get_country_bounding_box_not_found(mock_get):
    response = MagicMock()
    response.status_code = 200
    response.raise_for_status = MagicMock()
    response.json.return_value = []
    mock_get.return_value = response

    api = AeroplanesAPI()
    with pytest.raises(ValueError, match="не найдена"):
        api._get_country_bounding_box("Unknownland")


@patch("src.aeroplanes_api.requests.Session")
def test_connect_failure(mock_session_cls):
    session = MagicMock()
    mock_session_cls.return_value = session
    session.get.side_effect = requests.RequestException("timeout")

    api = AeroplanesAPI()
    with pytest.raises(ConnectionError):
        api._connect()


def test_empty_country_raises():
    api = AeroplanesAPI()
    with pytest.raises(ValueError):
        api._get_country_bounding_box("  ")
