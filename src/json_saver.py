"""JSON-файловое хранилище данных о самолётах."""

import json
from pathlib import Path
from typing import Any

from src.abstract_storage import AbstractStorage
from src.aeroplane import Aeroplane


class JSONSaver(AbstractStorage):
    """Сохранение и чтение данных о самолётах в JSON-файле."""

    DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "aeroplanes.json"

    def __init__(self, file_path: str | Path | None = None) -> None:
        self._file_path = Path(file_path) if file_path else self.DEFAULT_PATH

    def _ensure_file_exists(self) -> None:
        """Создать файл и каталог при первом обращении."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._write_data([])

    def _read_data(self) -> list[dict[str, Any]]:
        """Прочитать список словарей из JSON."""
        self._ensure_file_exists()
        try:
            with self._file_path.open(encoding="utf-8") as file:
                content = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Файл {self._file_path} содержит некорректный JSON"
            ) from exc
        except OSError as exc:
            raise OSError(f"Не удалось прочитать файл {self._file_path}") from exc

        if not isinstance(content, list):
            raise ValueError("JSON-файл должен содержать список объектов")
        return content

    def _write_data(self, records: list[dict[str, Any]]) -> None:
        """Записать список словарей в JSON."""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._file_path.open("w", encoding="utf-8") as file:
                json.dump(records, file, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise OSError(f"Не удалось записать файл {self._file_path}") from exc

    def _records_to_aeroplanes(self, records: list[dict[str, Any]]) -> list[Aeroplane]:
        """Преобразовать записи файла в объекты Aeroplane."""
        aeroplanes: list[Aeroplane] = []
        for record in records:
            try:
                aeroplanes.append(Aeroplane.from_dict(record))
            except (TypeError, ValueError):
                continue
        return aeroplanes

    def _find_index(self, records: list[dict[str, Any]], aeroplane: Aeroplane) -> int:
        """Найти индекс записи по icao24 или позывному."""
        for index, record in enumerate(records):
            if aeroplane.icao24 and record.get("icao24") == aeroplane.icao24:
                return index
            if record.get("callsign", "").upper() == aeroplane.callsign.upper():
                return index
        return -1

    def load_aeroplanes_from_file(self) -> list[Aeroplane]:
        """
        Считать все данные из JSON-файла и вернуть список объектов Aeroplane.

        Фильтрация и сортировка выполняются отдельными функциями (шаг 4),
        которым передаётся полученный список.
        """
        records = self._read_data()
        return self._records_to_aeroplanes(records)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолёт или обновить существующую запись."""
        records = self._read_data()
        index = self._find_index(records, aeroplane)
        payload = aeroplane.to_dict()
        if index >= 0:
            records[index] = payload
        else:
            records.append(payload)
        self._write_data(records)

    def get_aeroplanes(self, **criteria: Any) -> list[Aeroplane]:
        """
        Получить самолёты из файла.

        Без критериев возвращает все записи. Критерии поиска — для совместимости
        с будущим коннектором БД; для файла рекомендуется load_aeroplanes_from_file()
        и функции фильтрации из services.
        """
        aeroplanes = self.load_aeroplanes_from_file()
        if not criteria:
            return aeroplanes

        country = criteria.get("origin_country") or criteria.get("country")
        if country:
            needle = str(country).strip().lower()
            aeroplanes = [
                plane
                for plane in aeroplanes
                if plane.origin_country.lower() == needle
                or needle in plane.origin_country.lower()
            ]

        callsign = criteria.get("callsign")
        if callsign:
            needle = str(callsign).strip().upper()
            aeroplanes = [
                plane for plane in aeroplanes if plane.callsign.upper() == needle
            ]

        return aeroplanes

    def get_aeroplanes_by_country(self, country: str) -> list[Aeroplane]:
        """Получить самолёты по стране регистрации (обёртка для совместимости)."""
        if not country or not country.strip():
            raise ValueError("Страна для фильтрации не может быть пустой")
        return self.get_aeroplanes(origin_country=country.strip())

    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """Удалить самолёт по объекту."""
        records = self._read_data()
        index = self._find_index(records, aeroplane)
        if index < 0:
            return False
        records.pop(index)
        self._write_data(records)
        return True

    def delete_aeroplane_by_callsign(self, callsign: str) -> bool:
        """Удалить самолёт по позывному."""
        if not callsign or not callsign.strip():
            raise ValueError("Позывной для удаления не может быть пустым")
        return self.delete_aeroplane(
            Aeroplane(
                callsign=callsign.strip(),
                origin_country="Unknown",
                velocity=0.0,
                baro_altitude=0.0,
            )
        )
