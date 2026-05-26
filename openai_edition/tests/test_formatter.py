from openai_edition.utils.formatter import (
    format_date_only,
    format_datetime,
    format_delay,
    format_flight,
    format_flight_status,
    format_time_only,
    truncate,
)


def test_format_flight_status_known_unknown_and_empty():
    assert format_flight_status("active") == "[IN FLIGHT]"
    assert format_flight_status("mystery") == "[MYSTERY]"
    assert format_flight_status("") == "[UNKNOWN]"
    assert format_flight_status(None) == "[UNKNOWN]"


def test_format_datetime_helpers():
    iso = "2024-06-01T14:30:00+00:00"
    assert format_datetime(iso) == "2024-06-01 14:30"
    assert format_time_only(iso) == "14:30"
    assert format_date_only(iso) == "2024-06-01"

    assert format_datetime("bad") == "bad"
    assert format_time_only("bad") == "-"
    assert format_date_only("bad") == "-"
    assert format_datetime(None) == "-"


def test_format_delay_values():
    assert format_delay(None) == "none"
    assert format_delay(0) == "none"
    assert format_delay(20) == "+20 min"
    assert format_delay(-5) == "-5 min"


def test_truncate_behavior():
    assert truncate("short", max_len=10) == "short"
    assert truncate("", max_len=10) == "-"
    assert truncate(None, max_len=10) == "-"
    assert truncate("abcdefghijklmnopqrstuvwxyz", max_len=10) == "abcdefg..."


def test_format_flight_with_partial_payload():
    raw = {
        "flight_status": "active",
        "flight": {"iata": "SU100"},
        "departure": {"scheduled": "2024-06-01T14:30:00+00:00"},
    }

    formatted = format_flight(raw)

    assert formatted["flight_iata"] == "SU100"
    assert formatted["flight_icao"] == "-"
    assert formatted["status"] == "[IN FLIGHT]"
    assert formatted["airline_name"] == "-"
    assert formatted["dep_scheduled"] == "14:30"
    assert formatted["dep_actual"] == "-"
    assert formatted["arr_scheduled"] == "-"
    assert formatted["dep_delay"] == "none"
    assert formatted["arr_delay"] == "none"
    assert formatted["altitude"] == "-"
    assert formatted["speed"] == "-"
    assert formatted["is_grounded"] is False

