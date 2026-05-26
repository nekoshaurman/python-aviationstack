from datetime import datetime


# ------------------------------------------------------------------ #
#  Flight status labels                                                #
# ------------------------------------------------------------------ #

FLIGHT_STATUS_MAP = {
    "scheduled": "ON TIME",
    "active":    "IN FLIGHT",
    "landed":    "LANDED",
    "cancelled": "CANCELLED",
    "incident":  "INCIDENT",
    "diverted":  "DIVERTED",
}


def format_flight_status(status: str) -> str:
    """
    Convert raw API status to a bracketed text label.
    Example: 'active' -> '[IN FLIGHT]'
    """
    if not status:
        return "[UNKNOWN]"
    label = FLIGHT_STATUS_MAP.get(status.lower(), status.upper())
    return f"[{label}]"


# ------------------------------------------------------------------ #
#  Date / time helpers                                                 #
# ------------------------------------------------------------------ #

def format_datetime(iso_string: str | None) -> str:
    """
    Format an ISO datetime string for display.
    '2024-06-01T14:30:00+00:00' -> '2024-06-01 14:30'
    """
    if not iso_string:
        return "-"
    try:
        clean = iso_string[:16].replace("T", " ")
        dt = datetime.strptime(clean, "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_string or "-"


def format_time_only(iso_string: str | None) -> str:
    """
    Extract time only from an ISO string.
    '2024-06-01T14:30:00+00:00' -> '14:30'
    """
    if not iso_string:
        return "-"
    try:
        clean = iso_string[:16]
        dt = datetime.strptime(clean, "%Y-%m-%dT%H:%M")
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return "-"


def format_date_only(iso_string: str | None) -> str:
    """
    Extract date only from an ISO string.
    '2024-06-01T14:30:00+00:00' -> '2024-06-01'
    """
    if not iso_string:
        return "-"
    try:
        clean = iso_string[:10]
        dt = datetime.strptime(clean, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "-"


def format_delay(minutes: int | None) -> str:
    """
    Format a delay value in minutes.
    None or 0 -> 'none'
    20        -> '+20 min'
    -5        -> '-5 min'
    """
    if not minutes:
        return "none"
    sign = "+" if minutes > 0 else ""
    return f"{sign}{minutes} min"


def format_history_datetime(iso_string: str | None) -> str:
    """
    Format a history record timestamp.
    '2024-06-01T14:30:00.123456' -> '2024-06-01 14:30'
    """
    if not iso_string:
        return "-"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return iso_string or "-"


# ------------------------------------------------------------------ #
#  Flight data                                                         #
# ------------------------------------------------------------------ #

def format_flight(flight: dict) -> dict:
    """
    Normalize raw API flight data into display-ready strings.
    Returns a flat dict of formatted values.
    """
    dep = flight.get("departure") or {}
    arr = flight.get("arrival") or {}
    airline = flight.get("airline") or {}
    fl = flight.get("flight") or {}
    aircraft = flight.get("aircraft") or {}
    live = flight.get("live") or {}

    return {
        "flight_iata":   fl.get("iata") or "-",
        "flight_icao":   fl.get("icao") or "-",

        "airline_name":  airline.get("name") or "-",
        "airline_iata":  airline.get("iata") or "-",

        "status":        format_flight_status(flight.get("flight_status")),
        "status_raw":    flight.get("flight_status") or "-",

        "dep_airport":   dep.get("airport") or "-",
        "dep_iata":      dep.get("iata") or "-",
        "dep_scheduled": format_time_only(dep.get("scheduled")),
        "dep_actual":    format_time_only(dep.get("actual")),
        "dep_delay":     format_delay(dep.get("delay")),
        "dep_terminal":  dep.get("terminal") or "-",
        "dep_gate":      dep.get("gate") or "-",

        "arr_airport":   arr.get("airport") or "-",
        "arr_iata":      arr.get("iata") or "-",
        "arr_scheduled": format_time_only(arr.get("scheduled")),
        "arr_actual":    format_time_only(arr.get("actual")),
        "arr_estimated": format_time_only(arr.get("estimated")),
        "arr_delay":     format_delay(arr.get("delay")),
        "arr_terminal":  arr.get("terminal") or "-",
        "arr_gate":      arr.get("gate") or "-",

        "aircraft_reg":  aircraft.get("registration") or "-",
        "aircraft_type": aircraft.get("iata") or "-",

        "altitude":      f"{live.get('altitude', '-')} m" if live.get("altitude") else "-",
        "speed":         f"{live.get('speed_horizontal', '-')} km/h" if live.get("speed_horizontal") else "-",
        "is_grounded":   live.get("is_ground", False),
    }


def format_airport(airport: dict) -> dict:
    """Normalize raw API airport data into display-ready strings."""
    return {
        "name":        airport.get("airport_name") or "-",
        "iata":        airport.get("iata_code") or "-",
        "icao":        airport.get("icao_code") or "-",
        "city":        airport.get("city_iata_code") or "-",
        "country":     airport.get("country_name") or "-",
        "country_iso": airport.get("country_iso2") or "-",
        "timezone":    airport.get("timezone") or "-",
        "latitude":    airport.get("latitude") or "-",
        "longitude":   airport.get("longitude") or "-",
        "phone":       airport.get("phone_number") or "-",
    }


def format_airline(airline: dict) -> dict:
    """Normalize raw API airline data into display-ready strings."""
    return {
        "name":          airline.get("airline_name") or "-",
        "iata":          airline.get("iata_code") or "-",
        "icao":          airline.get("icao_code") or "-",
        "country":       airline.get("country_name") or "-",
        "country_iso":   airline.get("country_iso2") or "-",
        "callsign":      airline.get("callsign") or "-",
        "hub":           airline.get("hub_code") or "-",
        "status":        airline.get("status") or "-",
        "founded":       airline.get("date_founded") or "-",
        "fleet_size":    str(airline.get("fleet_size") or "-"),
        "fleet_avg_age": str(airline.get("fleet_average_age") or "-"),
    }


# ------------------------------------------------------------------ #
#  Utilities                                                           #
# ------------------------------------------------------------------ #

def truncate(text: str, max_len: int = 30) -> str:
    """Truncate long strings with an ellipsis."""
    if not text or len(text) <= max_len:
        return text or "-"
    return text[:max_len - 3] + "..."
