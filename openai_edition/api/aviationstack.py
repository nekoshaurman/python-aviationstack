import os
import json
import requests
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

console = Console()

# Global flag — set by --raw CLI option
RAW_MODE: bool = False


class AviationStackError(Exception):
    """Base exception for AviationStack API errors."""
    pass


class AviationStackClient:
    """
    AviationStack API client.
    Docs: https://aviationstack.com/documentation

    Free plan limits:
    - 100 requests/month
    - No historical data
    - No route data
    - /airports and /airlines endpoints are paid-only
    """

    BASE_URL = "http://api.aviationstack.com/v1"

    def __init__(self, raw: bool = False):
        self.raw = raw or RAW_MODE
        self.api_key = os.getenv("AVIATION_API_KEY")
        if not self.api_key:
            raise AviationStackError(
                "AVIATION_API_KEY not found. "
                "Check your .env file."
            )

    def _get(self, endpoint: str, params: dict) -> dict:
        """Base GET request. Injects access_key automatically."""
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
                title="[bold white]-- REQUEST[/bold white]",
                border_style="white",
                expand=False,
            ))
        else:
            console.print("[dim]--- sending request...[/dim]")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise AviationStackError("No internet connection.")
        except requests.exceptions.Timeout:
            raise AviationStackError("Server did not respond within 10 seconds. Try again later.")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code
            if self.raw:
                _print_raw_response(e.response)
            if status == 429:
                raise AviationStackError(
                    "Rate limit exceeded. "
                    "Quota resets at the start of next month."
                )
            if status == 403:
                raise AviationStackError(
                    "This endpoint is not available on the free plan. "
                    "Only /flights is accessible."
                )
            raise AviationStackError(f"HTTP error: {status}")

        data = response.json()

        if self.raw:
            _print_raw_response(response)
        else:
            console.print("[dim]--- done[/dim]")

        # AviationStack may return errors inside JSON with HTTP 200
        if "error" in data:
            error = data["error"]
            code = error.get("code", "unknown")
            info = error.get("info", "Unknown error")
            if code == "usage_limit_reached":
                raise AviationStackError(
                    "Rate limit exceeded. "
                    "Quota resets at the start of next month."
                )
            raise AviationStackError(f"[{code}] {info}")

        return data

    # ------------------------------------------------------------------ #
    #  Flights                                                             #
    # ------------------------------------------------------------------ #

    def get_flight(self, flight_iata: str) -> dict | None:
        data = self._get("flights", {"flight_iata": flight_iata})
        return data.get("data", [None])[0] if data.get("data") else None

    def get_flights_by_airline(self, airline_iata: str, limit: int = 10) -> list:
        data = self._get("flights", {"airline_iata": airline_iata, "limit": limit})
        return data.get("data", [])

    # ------------------------------------------------------------------ #
    #  Airports                                                            #
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
    #  Airlines                                                            #
    # ------------------------------------------------------------------ #

    def get_airline(self, iata_code: str) -> dict | None:
        """
        Fetch airline info by IATA code.

        Checks local cache first to avoid spending quota.
        Falls back to paginated /airlines scan if not cached.
        """
        from openai_edition.db.database import airline_cache_get, airline_cache_set

        iata_upper = iata_code.upper()

        cached = airline_cache_get(iata_upper)
        if cached:
            console.print("[dim]--- loaded from cache[/dim]")
            return cached

        limit = 100
        offset = 0
        result = None

        while True:
            data = self._get("airlines", {"limit": limit, "offset": offset})
            airlines = data.get("data", [])

            if not airlines:
                break

            for airline in airlines:
                code = airline.get("iata_code")
                if not code:
                    continue
                airline_cache_set(code.upper(), airline)
                if code.upper() == iata_upper:
                    result = airline

            if result:
                break

            pagination = data.get("pagination", {})
            total = pagination.get("total", 0)
            offset += limit

            if offset >= total:
                break

        return result


# ------------------------------------------------------------------ #
#  Raw response printer                                               #
# ------------------------------------------------------------------ #

def _print_raw_response(response: requests.Response) -> None:
    status = response.status_code
    status_style = "bold white" if status == 200 else "bold white"

    console.print(
        f"[{status_style}]HTTP {status}[/{status_style}]",
        end="  ",
    )
    url_display = response.url[:80] + "..." if len(response.url) > 80 else response.url
    console.print(f"[dim]{url_display}[/dim]")

    try:
        body = json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception:
        body = response.text

    syntax = Syntax(body, "json", theme="ansi_dark", line_numbers=False)
    console.print(Panel(
        syntax,
        title=f"[bold white]-- RESPONSE [{status}][/bold white]",
        border_style="white",
        expand=False,
    ))
