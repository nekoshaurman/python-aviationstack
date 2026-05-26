import os
import json
import requests
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

console = Console()


class AviationStackError(Exception):
    """Базовое исключение для ошибок AviationStack API."""
    pass


class AviationStackClient:
    """
    Клиент для работы с AviationStack API.
    Документация: https://aviationstack.com/documentation

    Бесплатный план:
    - HTTPS доступен на всех планах
    - 100 запросов в месяц
    - Нет исторических данных
    - Нет данных о маршрутах
    """

    BASE_URL = "http://api.aviationstack.com/v1"

    def __init__(self, raw: bool = False):
        self.raw = raw
        self.api_key = os.getenv("AVIATION_API_KEY")
        if not self.api_key:
            raise AviationStackError(
                "AVIATION_API_KEY не найден. "
                "Проверь файл .env"
            )

    def _get(self, endpoint: str, params: dict) -> dict:
        """
        Базовый GET-запрос к API.
        Автоматически добавляет access_key ко всем запросам.
        """
        params["access_key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"

        if self.raw:
            safe_params = {
                k: ("***" if k == "access_key" else v)
                for k, v in params.items()
            }
            req = requests.Request("GET", url, params=safe_params)
            prepared = req.prepare()
            console.print(Panel(
                f"[bold]GET[/bold] {prepared.url}",
                title="[bold yellow]──  REQUEST[/bold yellow]",
                border_style="yellow",
                expand=False,
            ))
        else:
            console.print("[dim]─── Отправка запроса к API…[/dim]")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise AviationStackError("Нет соединения с интернетом.")
        except requests.exceptions.Timeout:
            raise AviationStackError("Сервер не ответил за 10 секунд. Попробуй позже.")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if self.raw:
                _print_raw_response(e.response)
            if status == 429:
                raise AviationStackError(
                    "Лимит запросов исчерпан. "
                    "Лимит обновляется в начале следующего месяца."
                )
            if status == 403:
                raise AviationStackError(
                    "Этот эндпоинт недоступен на бесплатном плане. "
                    "Доступен только эндпоинт /flights."
                )
            raise AviationStackError(f"HTTP ошибка: {status}")

        data = response.json()

        if self.raw:
            _print_raw_response(response)
        else:
            console.print("[dim]─── Запрос выполнен ✓[/dim]")

        # AviationStack возвращает некоторые ошибки внутри JSON с кодом 200
        if "error" in data:
            error = data["error"]
            code = error.get("code", "unknown")
            info = error.get("info", "Неизвестная ошибка")
            if code == "usage_limit_reached":
                raise AviationStackError(
                    "Лимит запросов исчерпан. "
                    "Лимит обновляется в начале следующего месяца."
                )
            raise AviationStackError(f"[{code}] {info}")

        return data

    # ------------------------------------------------------------------ #
    #  Рейсы                                                               #
    # ------------------------------------------------------------------ #

    def get_flight(self, flight_iata: str) -> dict | None:
        data = self._get("flights", {"flight_iata": flight_iata})
        return data.get("data", [None])[0] if data.get("data") else None

    def get_flights_by_airline(self, airline_iata: str, limit: int = 10) -> list:
        data = self._get("flights", {"airline_iata": airline_iata, "limit": limit})
        return data.get("data", [])

    # ------------------------------------------------------------------ #
    #  Аэропорты                                                           #
    # ------------------------------------------------------------------ #

    def get_airport(self, iata_code: str) -> dict | None:
        data = self._get("airports", {"search": iata_code})
        airports = data.get("data", [])
        for airport in airports:
            if airport.get("iata_code", "").upper() == iata_code.upper():
                return airport
        return airports[0] if airports else None

    def get_arrivals(self, airport_iata: str, limit: int = 10) -> list:
        data = self._get("flights", {"arr_iata": airport_iata, "limit": limit})
        return data.get("data", [])

    def get_departures(self, airport_iata: str, limit: int = 10) -> list:
        data = self._get("flights", {"dep_iata": airport_iata, "limit": limit})
        return data.get("data", [])

    # ------------------------------------------------------------------ #
    #  Авиакомпании                                                        #
    # ------------------------------------------------------------------ #

    def get_airline(self, iata_code: str) -> dict | None:
        """
        Получить информацию об авиакомпании по коду IATA.

        Сначала проверяем локальный кеш — если есть, токен не тратим.
        Если нет — грузим /airlines постранично и ищем локально,
        т.к. параметр search доступен только на платном плане.
        """
        from claude.db.database import airline_cache_get, airline_cache_set

        iata_upper = iata_code.upper()

        # Проверяем кеш
        cached = airline_cache_get(iata_upper)
        if cached:
            console.print("[dim]─── Загружено из кеша ✓[/dim]")
            return cached

        # Не нашли в кеше — идём в API
        limit = 100
        offset = 0
        result = None

        while True:
            data = self._get("airlines", {"limit": limit, "offset": offset})
            airlines = data.get("data", [])

            if not airlines:
                break

            # Кешируем все полученные авиакомпании за один проход
            for airline in airlines:
                code = airline.get("iata_code")
                if not code:
                    continue
                airline_cache_set(code.upper(), airline)
                if code.upper() == iata_upper:
                    result = airline

            # Если нашли нужную — дальше не листаем
            if result:
                break

            pagination = data.get("pagination", {})
            total = pagination.get("total", 0)
            offset += limit

            if offset >= total:
                break

        return result


# ------------------------------------------------------------------ #
#  Вспомогательная функция вывода ответа                              #
# ------------------------------------------------------------------ #

def _print_raw_response(response: requests.Response) -> None:
    status = response.status_code
    status_color = "green" if status == 200 else "red"

    console.print(
        f"[bold {status_color}]HTTP {status}[/bold {status_color}]",
        end="  ",
    )
    url_display = response.url[:80] + "…" if len(response.url) > 80 else response.url
    console.print(f"[dim]{url_display}[/dim]")

    try:
        body = json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception:
        body = response.text

    syntax = Syntax(body, "json", theme="monokai", line_numbers=False)
    console.print(Panel(
        syntax,
        title=f"[bold yellow]──  RESPONSE  [{status}][/bold yellow]",
        border_style="yellow",
        expand=False,
    ))