"""Абстрактный класс для работы с внешними API."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractAPI(ABC):
    """Базовый интерфейс для клиентов внешних API."""

    @abstractmethod
    def _connect(self) -> None:
        """Проверить доступность API и подготовить соединение."""

    @abstractmethod
    def _get_country_bounding_box(self, country: str) -> tuple[float, float, float, float]:
        """
        Получить координаты ограничивающего прямоугольника страны.

        Returns:
            Кортеж (min_lat, max_lat, min_lon, max_lon).
        """

    @abstractmethod
    def _fetch_aeroplanes_in_area(
        self, bounding_box: tuple[float, float, float, float]
    ) -> dict[str, Any]:
        """Получить ответ OpenSky (states, time) для заданной области."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[list[Any]]:
        """Получить информацию о самолётах в воздушном пространстве страны."""
