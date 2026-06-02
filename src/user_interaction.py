"""Консольное взаимодействие с пользователем."""

from src.aeroplane import Aeroplane
from src.aeroplanes_api import AeroplanesAPI
from src.json_saver import JSONSaver
from src.services import (
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)


def _read_positive_int(prompt: str) -> int:
    """Запросить у пользователя положительное целое число."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Введите целое число больше нуля.")


def _load_saved_planes(json_saver: JSONSaver) -> list[Aeroplane]:
    """Загрузить из файла список объектов Aeroplane."""
    return json_saver.load_aeroplanes_from_file()


def _fetch_and_save_planes(json_saver: JSONSaver) -> None:
    """Получить данные из API и сохранить в JSON."""
    country = input("Введите страну: ").strip()
    if not country:
        print("Название страны не может быть пустым.")
        return

    api = AeroplanesAPI()
    try:
        raw_data = api.get_aeroplanes(country)
        new_planes = Aeroplane.cast_to_object_list(raw_data)
        if not new_planes and api.aeroplanes:
            new_planes = Aeroplane.cast_to_object_list(api.aeroplanes)
    except (ConnectionError, ValueError) as exc:
        print(f"Ошибка при получении данных: {exc}")
        return

    if not new_planes:
        print("Самолёты в указанном регионе не найдены.")
        return

    for plane in new_planes:
        json_saver.add_aeroplane(plane)

    print(f"Данные по стране «{country}» добавлены/обновлены в файле.")


def _show_top_by_altitude(saved_planes: list[Aeroplane]) -> None:
    """Топ N по высоте: фильтрация функциями шага 4."""
    if not saved_planes:
        print("Нет сохранённых данных. Сначала загрузите данные из API (п. 1).")
        return

    top_n = _read_positive_int("Введите количество самолётов для топ N: ")
    filter_words_raw = input(
        "Введите страны регистрации для фильтрации (через пробел, Enter — без фильтра): "
    ).strip()
    filter_words = filter_words_raw.split() if filter_words_raw else []

    altitude_input = input(
        "Введите диапазон высот (например: 1000 - 10000, Enter — без фильтра): "
    ).strip()

    try:
        filtered = filter_aeroplanes(saved_planes, filter_words)
        if altitude_input:
            filtered = get_aeroplanes_by_altitude(filtered, altitude_input)
        top_planes = get_top_aeroplanes(filtered, top_n)
    except ValueError as exc:
        print(f"Ошибка фильтрации: {exc}")
        return

    print(f"\nТоп {top_n} самолётов по высоте (по убыванию):")
    print_aeroplanes(top_planes)


def user_interaction() -> None:
    """Главное меню: API или работа с данными из файла."""
    json_saver = JSONSaver()

    while True:
        print("\n=== Трекер самолётов ===")
        print("1. Получить данные о самолётах из API по стране")
        print("2. Показать все сохранённые самолёты")
        print("3. Найти самолёты по стране регистрации в сохранённых")
        print("4. Удалить самолёт из сохранённых по позывному")
        print("5. Топ N самолётов по высоте (фильтрация и сортировка)")
        print("6. Выйти")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            _fetch_and_save_planes(json_saver)

        elif choice == "2":
            saved_planes = _load_saved_planes(json_saver)
            sorted_planes = sort_aeroplanes(
                saved_planes, by="baro_altitude", descending=True
            )
            print_aeroplanes(sorted_planes)

        elif choice == "3":
            country = input("Введите страну регистрации: ").strip()
            if not country:
                print("Страна не может быть пустой.")
                continue
            saved_planes = _load_saved_planes(json_saver)
            planes_from_file = filter_aeroplanes(saved_planes, [country])
            print(f"\nСамолёты со страной регистрации «{country}»:")
            print_aeroplanes(planes_from_file)

        elif choice == "4":
            callsign = input("Введите позывной для удаления: ").strip()
            if not callsign:
                print("Позывной не может быть пустым.")
                continue
            try:
                deleted = json_saver.delete_aeroplane_by_callsign(callsign)
            except ValueError as exc:
                print(f"Ошибка: {exc}")
                continue
            if deleted:
                print(f"Самолёт с позывным «{callsign}» удалён.")
            else:
                print(f"Самолёт с позывным «{callsign}» удален (если существовал).")

        elif choice == "5":
            saved_planes = _load_saved_planes(json_saver)
            _show_top_by_altitude(saved_planes)

        elif choice == "6":
            print("До свидания!")
            break

        else:
            print("Неверный пункт меню. Выберите число от 1 до 6.")
