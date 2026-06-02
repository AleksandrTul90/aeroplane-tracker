"""Клиент API Nominatim и OpenSky Network."""

from typing import Any

import requests
from requests import get

from src.abstract_api import AbstractAPI


class AeroplanesAPI(AbstractAPI):
    """Получение координат стран и данных о самолётах."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"
    USER_AGENT = "test-app/1.0"

    def __init__(self) -> None:
        self.aeroplanes: dict[str, Any] | list[list[Any]] | None = None
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})

    def _connect(self) -> None:
        """Проверить доступность сервисов."""
        try:
            response = self._session.get(
                self.NOMINATIM_URL,
                params={"country": "Spain", "format": "json", "limit": 1},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ConnectionError(
                "Не удалось подключиться к Nominatim API"
            ) from exc

    def _get_country_bounding_box(
        self, country: str
    ) -> tuple[float, float, float, float]:
        """Запросить bounding box страны через Nominatim."""
        if not country or not country.strip():
            raise ValueError("Название страны не может быть пустым")

        headers = {"User-Agent": self.USER_AGENT}
        params = {
            "country": country.strip(),
            "format": "json",
            "limit": 1,
        }

        try:
            response = get(
                self.NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise ConnectionError(
                f"Ошибка при запросе координат для «{country}»"
            ) from exc
        except ValueError as exc:
            raise ConnectionError("Некорректный ответ Nominatim") from exc

        if not data:
            raise ValueError(f"Страна «{country}» не найдена")

        geo_coordinates = data[0].get("boundingbox")
        if not geo_coordinates or len(geo_coordinates) != 4:
            raise ValueError(f"Для страны «{country}» не получен boundingbox")

        # Порядок Nominatim: [south, north, west, east]
        south, north, west, east = (float(value) for value in geo_coordinates)
        return south, north, west, east

    def _fetch_aeroplanes_in_area(
        self, bounding_box: tuple[float, float, float, float]
    ) -> dict[str, Any]:
        """Запросить состояния воздушных судов в bounding box."""
        lamin, lamax, lomin, lomax = bounding_box

        params = {
            "lamin": lamin,
            "lamax": lamax,
            "lomin": lomin,
            "lomax": lomax,
        }

        try:
            response = get(self.OPENSKY_URL, params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise ConnectionError(
                "Ошибка при запросе данных OpenSky Network"
            ) from exc
        except ValueError as exc:
            raise ConnectionError("Некорректный ответ OpenSky Network") from exc

    def get_aeroplanes(self, country: str) -> list[list[Any]]:
        """Получить сырые состояния OpenSky для воздушного пространства страны."""
        self._connect()
        bounding_box = self._get_country_bounding_box(country)
        payload = self._fetch_aeroplanes_in_area(bounding_box)
        self.aeroplanes = payload
        states = payload.get("states")
        if states is None:
            return []
        return states


# Алиас в стиле примера из задания
APIAdapter = AeroplanesAPI
