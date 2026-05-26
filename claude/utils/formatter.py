from datetime import datetime


# ------------------------------------------------------------------ #
#  Статусы рейсов                                                      #
# ------------------------------------------------------------------ #

FLIGHT_STATUS_MAP = {
    "scheduled":  ("🔵", "По расписанию"),
    "active":     ("🟡", "В полёте"),
    "landed":     ("🟢", "Приземлился"),
    "cancelled":  ("🔴", "Отменён"),
    "incident":   ("🆘", "Инцидент"),
    "diverted":   ("🟠", "Перенаправлен"),
}


def format_flight_status(status: str) -> str:
    """
    Превратить статус из API в читаемый вид с эмодзи.
    Например: 'active' → '🟡 В полёте'
    """
    if not status:
        return "❓ Неизвестно"
    emoji, label = FLIGHT_STATUS_MAP.get(status.lower(), ("❓", status.capitalize()))
    return f"{emoji} {label}"


# ------------------------------------------------------------------ #
#  Время и даты                                                        #
# ------------------------------------------------------------------ #

def format_datetime(iso_string: str | None) -> str:
    """
    Форматировать ISO datetime строку в читаемый вид.
    '2024-06-01T14:30:00+00:00' → '01.06.2024 14:30'
    """
    if not iso_string:
        return "—"
    try:
        # Убираем таймзону для простоты отображения
        clean = iso_string[:16].replace("T", " ")
        dt = datetime.strptime(clean, "%Y-%m-%d %H:%M")
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return iso_string or "—"


def format_time_only(iso_string: str | None) -> str:
    """
    Извлечь только время из ISO строки.
    '2024-06-01T14:30:00+00:00' → '14:30'
    """
    if not iso_string:
        return "—"
    try:
        clean = iso_string[:16]
        dt = datetime.strptime(clean, "%Y-%m-%dT%H:%M")
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "—"


def format_date_only(iso_string: str | None) -> str:
    """
    Извлечь только дату из ISO строки.
    '2024-06-01T14:30:00+00:00' → '01.06.2024'
    """
    if not iso_string:
        return "—"
    try:
        clean = iso_string[:10]
        dt = datetime.strptime(clean, "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        return "—"


def format_delay(minutes: int | None) -> str:
    """
    Форматировать задержку в минутах.
    None или 0 → 'Нет'
    20        → '+20 мин'
    -5        → '-5 мин' (прилетел раньше)
    """
    if not minutes:
        return "Нет"
    sign = "+" if minutes > 0 else ""
    return f"{sign}{minutes} мин"


def format_duration(minutes: int | None) -> str:
    """
    Форматировать длительность полёта из минут.
    90  → '1ч 30м'
    45  → '45м'
    130 → '2ч 10м'
    """
    if not minutes:
        return "—"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}ч {mins}м" if mins else f"{hours}ч"
    return f"{mins}м"


def format_history_datetime(iso_string: str | None) -> str:
    """
    Форматировать дату из истории запросов.
    '2024-06-01T14:30:00.123456' → '01.06.2024 14:30'
    """
    if not iso_string:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return iso_string or "—"


# ------------------------------------------------------------------ #
#  Данные рейса                                                        #
# ------------------------------------------------------------------ #

def format_flight(flight: dict) -> dict:
    """
    Привести сырые данные рейса из API к удобному виду.
    Возвращает словарь с готовыми строками для отображения.
    """
    dep = flight.get("departure") or {}
    arr = flight.get("arrival") or {}
    airline = flight.get("airline") or {}
    fl = flight.get("flight") or {}
    aircraft = flight.get("aircraft") or {}
    live = flight.get("live") or {}

    return {
        # Рейс
        "flight_iata":    fl.get("iata") or "—",
        "flight_icao":    fl.get("icao") or "—",

        # Авиакомпания
        "airline_name":   airline.get("name") or "—",
        "airline_iata":   airline.get("iata") or "—",

        # Статус
        "status":         format_flight_status(flight.get("flight_status")),
        "status_raw":     flight.get("flight_status") or "—",

        # Вылет
        "dep_airport":    dep.get("airport") or "—",
        "dep_iata":       dep.get("iata") or "—",
        "dep_scheduled":  format_time_only(dep.get("scheduled")),
        "dep_actual":     format_time_only(dep.get("actual")),
        "dep_delay":      format_delay(dep.get("delay")),
        "dep_terminal":   dep.get("terminal") or "—",
        "dep_gate":       dep.get("gate") or "—",

        # Прилёт
        "arr_airport":    arr.get("airport") or "—",
        "arr_iata":       arr.get("iata") or "—",
        "arr_scheduled":  format_time_only(arr.get("scheduled")),
        "arr_actual":     format_time_only(arr.get("actual")),
        "arr_estimated":  format_time_only(arr.get("estimated")),
        "arr_delay":      format_delay(arr.get("delay")),
        "arr_terminal":   arr.get("terminal") or "—",
        "arr_gate":       arr.get("gate") or "—",

        # Самолёт
        "aircraft_reg":   aircraft.get("registration") or "—",
        "aircraft_type":  aircraft.get("iata") or "—",

        # Live данные (только для активных рейсов)
        "altitude":       f"{live.get('altitude', '—')} м" if live.get("altitude") else "—",
        "speed":          f"{live.get('speed_horizontal', '—')} км/ч" if live.get("speed_horizontal") else "—",
        "is_grounded":    live.get("is_ground", False),
    }


def format_airport(airport: dict) -> dict:
    """
    Привести сырые данные аэропорта к удобному виду.
    """
    return {
        "name":        airport.get("airport_name") or "—",
        "iata":        airport.get("iata_code") or "—",
        "icao":        airport.get("icao_code") or "—",
        "city":        airport.get("city_iata_code") or "—",
        "country":     airport.get("country_name") or "—",
        "country_iso": airport.get("country_iso2") or "—",
        "timezone":    airport.get("timezone") or "—",
        "latitude":    airport.get("latitude") or "—",
        "longitude":   airport.get("longitude") or "—",
        "phone":       airport.get("phone_number") or "—",
    }


def format_airline(airline: dict) -> dict:
    """
    Привести сырые данные авиакомпании к удобному виду.
    """
    return {
        "name":         airline.get("airline_name") or "—",
        "iata":         airline.get("iata_code") or "—",
        "icao":         airline.get("icao_code") or "—",
        "country":      airline.get("country_name") or "—",
        "country_iso":  airline.get("country_iso2") or "—",
        "callsign":     airline.get("callsign") or "—",
        "hub":          airline.get("hub_code") or "—",
        "status":       airline.get("status") or "—",
        "founded":      airline.get("date_founded") or "—",
        "fleet_size":   str(airline.get("fleet_size") or "—"),
        "fleet_avg_age": str(airline.get("fleet_average_age") or "—"),
    }


# ------------------------------------------------------------------ #
#  Утилиты                                                             #
# ------------------------------------------------------------------ #

def truncate(text: str, max_len: int = 30) -> str:
    """
    Обрезать длинный текст с многоточием.
    'Очень длинное название аэропорта' → 'Очень длинное название аэро...'
    """
    if not text or len(text) <= max_len:
        return text or "—"
    return text[:max_len - 3] + "..."


def format_iata_upper(code: str) -> str:
    """
    Привести IATA код к верхнему регистру.
    """
    return code.upper().strip() if code else ""