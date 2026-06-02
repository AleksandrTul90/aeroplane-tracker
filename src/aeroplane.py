"""Модель воздушного судна."""

from __future__ import annotations

from functools import total_ordering
from typing import Any


@total_ordering
class Aeroplane:
    """
    Информация о самолёте.

    Каждый самолёт — отдельный объект с позывным, страной, скоростью и высотой.
    Сравнение через методы экземпляра: в метод передаются self и other.
    """

    VALID_COMPARE_FIELDS = ("baro_altitude", "velocity")

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        baro_altitude: float,
        icao24: str = "",
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        self.icao24 = self._validate_icao24(icao24)
        self.callsign = self._validate_callsign(callsign)
        self.origin_country = self._validate_country(origin_country)
        self.velocity = self._validate_velocity(velocity)
        self.baro_altitude = self._validate_altitude(baro_altitude)
        self.latitude = self._validate_coordinate(latitude, "latitude")
        self.longitude = self._validate_coordinate(longitude, "longitude")

    @staticmethod
    def _validate_other(other: object) -> Aeroplane:
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только с другим объектом Aeroplane")
        return other

    @staticmethod
    def _validate_callsign(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("Позывной должен быть строкой")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Позывной не может быть пустым")
        return cleaned

    @staticmethod
    def _validate_country(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("Страна регистрации должна быть строкой")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Страна регистрации не может быть пустой")
        return cleaned

    @staticmethod
    def _validate_velocity(value: float) -> float:
        if value is None:
            return 0.0
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Скорость должна быть числом") from exc
        if numeric < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return numeric

    @staticmethod
    def _validate_altitude(value: float) -> float:
        if value is None:
            return 0.0
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Высота должна быть числом") from exc
        return numeric

    @staticmethod
    def _validate_icao24(value: str) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise TypeError("ICAO24 должен быть строкой")
        return value.strip().lower()

    @staticmethod
    def _validate_coordinate(value: float | None, name: str) -> float | None:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} должна быть числом") from exc
        limit = 90 if name == "latitude" else 180
        if not -limit <= numeric <= limit:
            raise ValueError(f"{name} вне допустимого диапазона")
        return numeric

    def compare_by_speed(self, other: Aeroplane) -> int:
        """
        Сравнить текущий самолёт с другим по скорости.

        Args:
            other: второй экземпляр Aeroplane.

        Returns:
            -1 если self медленнее, 0 если равны, 1 если быстрее.
        """
        other = self._validate_other(other)
        if self.velocity < other.velocity:
            return -1
        if self.velocity > other.velocity:
            return 1
        return 0

    def compare_by_altitude(self, other: Aeroplane) -> int:
        """
        Сравнить текущий самолёт с другим по высоте.

        Args:
            other: второй экземпляр Aeroplane.
        """
        other = self._validate_other(other)
        if self.baro_altitude < other.baro_altitude:
            return -1
        if self.baro_altitude > other.baro_altitude:
            return 1
        return 0

    def is_faster_than(self, other: Aeroplane) -> bool:
        """Проверить, быстрее ли текущий самолёт, чем other."""
        return self.compare_by_speed(other) == 1

    def is_higher_than(self, other: Aeroplane) -> bool:
        """Проверить, выше ли текущий самолёт, чем other."""
        return self.compare_by_altitude(other) == 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.compare_by_altitude(other) == 0

    def __lt__(self, other: Aeroplane) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.compare_by_altitude(other) == -1

    def __gt__(self, other: Aeroplane) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.compare_by_altitude(other) == 1

    @classmethod
    def from_opensky_state(cls, state: list[Any]) -> Aeroplane | None:
        """Создать объект из одной записи ответа OpenSky."""
        if not state or len(state) < 10:
            return None

        callsign_raw = state[1]
        callsign = (callsign_raw or "").strip()
        if not callsign:
            callsign = (state[0] or "UNKNOWN").upper()

        return cls(
            callsign=callsign,
            origin_country=state[2] or "Unknown",
            velocity=state[9] if state[9] is not None else 0.0,
            baro_altitude=state[7] if state[7] is not None else 0.0,
            icao24=state[0] or "",
            latitude=state[6],
            longitude=state[5],
        )

    @classmethod
    def cast_to_object_list(
        cls, raw_data: list[list[Any]] | dict[str, Any] | None
    ) -> list[Aeroplane]:
        """Преобразовать ответ OpenSky в список объектов Aeroplane."""
        if raw_data is None:
            return []

        states: list[list[Any]] | None
        if isinstance(raw_data, dict):
            states = raw_data.get("states")
        else:
            states = raw_data

        if not states:
            return []

        result: list[Aeroplane] = []
        for state in states:
            try:
                aeroplane = cls.from_opensky_state(state)
            except (TypeError, ValueError):
                continue
            if aeroplane is not None:
                result.append(aeroplane)
        return result

    def to_dict(self) -> dict[str, Any]:
        """Сериализация для JSON-хранилища."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "baro_altitude": self.baro_altitude,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aeroplane:
        """Десериализация из словаря."""
        return cls(
            callsign=data.get("callsign", ""),
            origin_country=data.get("origin_country", ""),
            velocity=data.get("velocity", 0.0),
            baro_altitude=data.get("baro_altitude", 0.0),
            icao24=data.get("icao24", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )

    def __str__(self) -> str:
        lat = f"{self.latitude:.4f}" if self.latitude is not None else "—"
        lon = f"{self.longitude:.4f}" if self.longitude is not None else "—"
        return (
            f"{self.callsign} | {self.origin_country} | "
            f"скорость: {self.velocity:.1f} м/с | "
            f"высота: {self.baro_altitude:.1f} м | "
            f"коорд.: ({lat}, {lon})"
        )

    def __repr__(self) -> str:
        return (
            f"Aeroplane(callsign={self.callsign!r}, "
            f"origin_country={self.origin_country!r}, "
            f"velocity={self.velocity}, baro_altitude={self.baro_altitude})"
        )
