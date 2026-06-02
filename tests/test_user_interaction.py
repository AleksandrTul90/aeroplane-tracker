"""Тесты консольного меню (с моками ввода)."""

from unittest.mock import patch

from src.aeroplane import Aeroplane
from src.user_interaction import user_interaction


@patch("src.user_interaction.JSONSaver")
@patch("builtins.input")
def test_user_interaction_exit(mock_input, mock_saver_cls):
    mock_saver_cls.return_value.load_aeroplanes_from_file.return_value = []
    mock_input.side_effect = ["6"]
    user_interaction()


@patch("src.user_interaction.JSONSaver")
@patch("builtins.input")
def test_show_all_saved_planes(mock_input, mock_saver_cls):
    planes = [Aeroplane("A1", "Spain", 200.0, 8000.0)]
    mock_saver_cls.return_value.load_aeroplanes_from_file.return_value = planes
    mock_input.side_effect = ["2", "6"]
    user_interaction()
    mock_saver_cls.return_value.load_aeroplanes_from_file.assert_called()


@patch("src.user_interaction.filter_aeroplanes")
@patch("src.user_interaction.JSONSaver")
@patch("builtins.input")
def test_filter_by_country_uses_services(
    mock_input, mock_saver_cls, mock_filter
):
    planes = [
        Aeroplane("A1", "Spain", 200.0, 8000.0),
        Aeroplane("A2", "Germany", 250.0, 9000.0),
    ]
    mock_saver_cls.return_value.load_aeroplanes_from_file.return_value = planes
    mock_filter.return_value = [planes[0]]
    mock_input.side_effect = ["3", "Spain", "6"]
    user_interaction()
    mock_filter.assert_called_once_with(planes, ["Spain"])


@patch("src.user_interaction.AeroplanesAPI")
@patch("src.user_interaction.JSONSaver")
@patch("builtins.input")
def test_fetch_from_api(mock_input, mock_saver_cls, mock_api_cls):
    mock_api_cls.return_value.get_aeroplanes.return_value = [
        ["id", "TST1 ", "Spain", None, None, 0, 0, 5000, False, 200]
    ]
    mock_api_cls.return_value.aeroplanes = None
    mock_input.side_effect = ["1", "Spain", "6"]
    user_interaction()
    mock_saver_cls.return_value.add_aeroplane.assert_called()
