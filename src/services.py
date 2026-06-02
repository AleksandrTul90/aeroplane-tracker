"""Вспомогательные функции фильтрации и сортировки."""

from src.aeroplane import Aeroplane


def filter_aeroplanes(
    aeroplanes: list[Aeroplane], countries: list[str]
) -> list[Aeroplane]:
    """Отфильтровать самолёты по странам регистрации."""
    if not countries:
        return aeroplanes

    normalized = [country.strip().lower() for country in countries if country.strip()]
    if not normalized:
        return aeroplanes

    return [
        plane
        for plane in aeroplanes
        if any(
            country in plane.origin_country.lower() for country in normalized
        )
    ]


def parse_altitude_range(altitude_range: str) -> tuple[float, float]:
    """
    Разобрать диапазон высот.

    Поддерживаемые форматы: "1000 - 5000", "1000-5000", "1000,5000".
    """
    if not altitude_range or not altitude_range.strip():
        raise ValueError("Диапазон высот не может быть пустым")

    cleaned = altitude_range.strip().replace(",", " ")
    for separator in ("-", "—", "–"):
        if separator in cleaned:
            parts = cleaned.split(separator)
            if len(parts) == 2:
                try:
                    low = float(parts[0].strip())
                    high = float(parts[1].strip())
                except ValueError as exc:
                    raise ValueError(
                        "Диапазон высот должен содержать два числа"
                    ) from exc
                if low > high:
                    low, high = high, low
                return low, high

    parts = cleaned.split()
    if len(parts) != 2:
        raise ValueError(
            "Укажите диапазон в формате «мин - макс», например: 1000 - 5000"
        )

    try:
        low = float(parts[0])
        high = float(parts[1])
    except ValueError as exc:
        raise ValueError("Диапазон высот должен содержать два числа") from exc

    if low > high:
        low, high = high, low
    return low, high


def get_aeroplanes_by_altitude(
    aeroplanes: list[Aeroplane], altitude_range: str
) -> list[Aeroplane]:
    """Оставить самолёты, чья высота попадает в диапазон."""
    low, high = parse_altitude_range(altitude_range)
    return [
        plane for plane in aeroplanes if low <= plane.baro_altitude <= high
    ]


def sort_aeroplanes(
    aeroplanes: list[Aeroplane], by: str = "baro_altitude", descending: bool = True
) -> list[Aeroplane]:
    """Отсортировать самолёты по высоте или скорости."""
    if by not in Aeroplane.VALID_COMPARE_FIELDS:
        raise ValueError(f"Сортировка по полю «{by}» не поддерживается")
    return sorted(aeroplanes, key=lambda plane: getattr(plane, by), reverse=descending)


def get_top_aeroplanes(
    aeroplanes: list[Aeroplane], top_n: int, by: str = "baro_altitude"
) -> list[Aeroplane]:
    """Вернуть топ N самолётов (сортировка по убыванию)."""
    if top_n <= 0:
        raise ValueError("N должно быть положительным числом")
    sorted_planes = sort_aeroplanes(aeroplanes, by=by, descending=True)
    return sorted_planes[:top_n]


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:
    """Вывести список самолётов в консоль."""
    if not aeroplanes:
        print("Самолёты не найдены.")
        return
    for index, plane in enumerate(aeroplanes, start=1):
        print(f"{index}. {plane}")
