import sqlite3
import os
from datetime import datetime


# Путь к БД относительно этого файла
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "claude_aerotrack.db")


def get_connection() -> sqlite3.Connection:
    """
    Открыть соединение с БД.
    Создаёт файл и папку data/ если не существуют.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Результаты как dict-подобные объекты
    return conn


def init_db() -> None:
    """
    Инициализация БД — создать таблицы если не существуют.
    Вызывается один раз при старте приложения.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица watchlist — отслеживаемые рейсы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_iata TEXT    NOT NULL UNIQUE,
            added_at    TEXT    NOT NULL
        )
    """)

    # Таблица истории запросов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            command     TEXT    NOT NULL,
            query       TEXT    NOT NULL,
            result      TEXT,
            requested_at TEXT   NOT NULL
        )
    """)

    # Кеш авиакомпаний — чтобы не тратить токены на повторные запросы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS airline_cache (
            iata_code   TEXT    NOT NULL PRIMARY KEY,
            data        TEXT    NOT NULL,
            cached_at   TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------------ #
#  Watchlist                                                           #
# ------------------------------------------------------------------ #

def watchlist_add(flight_iata: str) -> bool:
    """
    Добавить рейс в watchlist.
    Возвращает True если добавлен, False если уже существует.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO watchlist (flight_iata, added_at) VALUES (?, ?)",
            (flight_iata.upper(), datetime.now().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # UNIQUE constraint — рейс уже в watchlist
        return False
    finally:
        conn.close()


def watchlist_remove(flight_iata: str) -> bool:
    """
    Удалить рейс из watchlist.
    Возвращает True если удалён, False если не был найден.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM watchlist WHERE flight_iata = ?",
        (flight_iata.upper(),)
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def watchlist_get_all() -> list[dict]:
    """
    Получить все рейсы из watchlist.
    Возвращает список словарей: [{id, flight_iata, added_at}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM watchlist ORDER BY added_at DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def watchlist_exists(flight_iata: str) -> bool:
    """
    Проверить есть ли рейс в watchlist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM watchlist WHERE flight_iata = ?",
        (flight_iata.upper(),)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# ------------------------------------------------------------------ #
#  История запросов                                                    #
# ------------------------------------------------------------------ #

def history_add(command: str, query: str, result: str = None) -> None:
    """
    Записать запрос в историю.

    command — название команды: flight, airport, airline
    query   — что искали: SU100, FRA, LH
    result  — краткий результат: "Найден", "Не найден", статус рейса
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history (command, query, result, requested_at)
        VALUES (?, ?, ?, ?)
        """,
        (command, query.upper(), result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def history_get_all(limit: int = 50) -> list[dict]:
    """
    Получить историю запросов.
    По умолчанию последние 50 записей.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM history ORDER BY requested_at DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def history_clear() -> int:
    """
    Очистить всю историю.
    Возвращает количество удалённых записей.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM history")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


# ------------------------------------------------------------------ #
#  Статистика                                                          #
# ------------------------------------------------------------------ #

def get_stats() -> dict:
    """
    Собрать статистику по всем таблицам.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Общее количество запросов
    cursor.execute("SELECT COUNT(*) FROM history")
    total_requests = cursor.fetchone()[0]

    # Запросы по командам
    cursor.execute("""
        SELECT command, COUNT(*) as count
        FROM history
        GROUP BY command
        ORDER BY count DESC
    """)
    by_command = {row["command"]: row["count"] for row in cursor.fetchall()}

    # Самые частые запросы
    cursor.execute("""
        SELECT query, COUNT(*) as count
        FROM history
        GROUP BY query
        ORDER BY count DESC
        LIMIT 5
    """)
    top_queries = [dict(row) for row in cursor.fetchall()]

    # Количество рейсов в watchlist
    cursor.execute("SELECT COUNT(*) FROM watchlist")
    watchlist_count = cursor.fetchone()[0]

    # Первый и последний запрос
    cursor.execute("SELECT MIN(requested_at), MAX(requested_at) FROM history")
    row = cursor.fetchone()
    first_request = row[0]
    last_request = row[1]

    conn.close()

    return {
        "total_requests": total_requests,
        "by_command": by_command,
        "top_queries": top_queries,
        "watchlist_count": watchlist_count,
        "first_request": first_request,
        "last_request": last_request,
    }

# ------------------------------------------------------------------ #
#  Кеш авиакомпаний                                                    #
# ------------------------------------------------------------------ #

def airline_cache_get(iata_code: str) -> dict | None:
    """
    Получить авиакомпанию из кеша.
    Возвращает dict с данными или None если не найдена.
    """
    import json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT data FROM airline_cache WHERE iata_code = ?",
        (iata_code.upper(),)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.loads(row["data"])
    return None


def airline_cache_set(iata_code: str, data: dict) -> None:
    """
    Сохранить авиакомпанию в кеш.
    Перезаписывает если уже существует.
    """
    import json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO airline_cache (iata_code, data, cached_at)
        VALUES (?, ?, ?)
        ON CONFLICT(iata_code) DO UPDATE SET
            data      = excluded.data,
            cached_at = excluded.cached_at
    """, (
        iata_code.upper(),
        json.dumps(data, ensure_ascii=False),
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()


def airline_cache_get_all() -> list[dict]:
    """
    Получить все закешированные авиакомпании.
    """
    import json
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT iata_code, cached_at FROM airline_cache ORDER BY cached_at DESC"
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def airline_cache_clear() -> int:
    """
    Очистить кеш авиакомпаний.
    Возвращает количество удалённых записей.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM airline_cache")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted