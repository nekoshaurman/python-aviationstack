from openai_edition.db import database


def test_init_db_creates_all_tables():
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = {row["name"] for row in cursor.fetchall()}
    conn.close()

    assert "watchlist" in table_names
    assert "history" in table_names
    assert "airline_cache" in table_names


def test_watchlist_add_exists_remove_cycle():
    assert database.watchlist_add("su100") is True
    assert database.watchlist_exists("SU100") is True

    assert database.watchlist_add("SU100") is False

    assert database.watchlist_remove("su100") is True
    assert database.watchlist_exists("SU100") is False
    assert database.watchlist_remove("SU100") is False


def test_history_add_get_all_and_clear():
    database.history_add("flight", "su100", "active")
    database.history_add("airport", "fra", "found")

    records = database.history_get_all(limit=10)
    assert len(records) == 2
    assert {r["command"] for r in records} == {"flight", "airport"}
    assert {r["query"] for r in records} == {"SU100", "FRA"}

    deleted = database.history_clear()
    assert deleted == 2
    assert database.history_get_all() == []


def test_airline_cache_set_get_and_clear():
    database.airline_cache_set("lh", {"airline_name": "Lufthansa", "iata_code": "LH"})
    database.airline_cache_set("su", {"airline_name": "Aeroflot", "iata_code": "SU"})

    assert database.airline_cache_get("LH")["airline_name"] == "Lufthansa"
    assert database.airline_cache_get("su")["airline_name"] == "Aeroflot"
    assert database.airline_cache_get("XX") is None

    all_items = database.airline_cache_get_all()
    assert {item["iata_code"] for item in all_items} == {"LH", "SU"}

    deleted = database.airline_cache_clear()
    assert deleted == 2
    assert database.airline_cache_get_all() == []


def test_get_stats_with_prepared_data():
    database.watchlist_add("SU100")
    database.watchlist_add("LH438")

    database.history_add("flight", "su100", "active")
    database.history_add("flight", "lh438", "landed")
    database.history_add("airport", "fra", "found")
    database.history_add("flight", "su100", "landed")

    stats = database.get_stats()

    assert stats["total_requests"] == 4
    assert stats["watchlist_count"] == 2
    assert stats["by_command"]["flight"] == 3
    assert stats["by_command"]["airport"] == 1
    assert stats["first_request"] is not None
    assert stats["last_request"] is not None

    top_queries = {item["query"]: item["count"] for item in stats["top_queries"]}
    assert top_queries["SU100"] == 2
    assert top_queries["LH438"] == 1
    assert top_queries["FRA"] == 1
