"""Абстрактный класс хранилища данных о самолётах."""

from abc import ABC, abstractmethod
from typing import Any

from src.aeroplane import Aeroplane


class AbstractStorage(ABC):
    """Интерфейс хранилища (файл, БД, удалённый сервис)."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить или обновить информацию о самолёте."""

    @abstractmethod
    def get_aeroplanes(self, **criteria: Any) -> list[Aeroplane]:
        """Получить самолёты по критериям поиска."""

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """Удалить самолёт по объекту."""

    @abstractmethod
    def delete_aeroplane_by_callsign(self, callsign: str) -> bool:
        """Удалить самолёт по позывному."""

    def update_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Обновить запись (заглушка для интеграции с БД)."""
        raise NotImplementedError(
            "Метод update_aeroplane предназначен для реализации в БД-коннекторе"
        )

    def execute_query(self, query: str) -> list[Aeroplane]:
        """Выполнить произвольный запрос (заглушка для БД)."""
        raise NotImplementedError(
            "Метод execute_query предназначен для реализации в БД-коннекторе"
        )
