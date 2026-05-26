import click
from rich.console import Console
from rich.table import Table
from rich import box

from openai_edition.api.aviationstack import AviationStackClient, AviationStackError
from openai_edition.db.database import (
    history_add,
    airline_cache_get_all,
    airline_cache_clear,
    airline_cache_get,
)
from openai_edition.utils.display import (
    print_airline,
    print_flights_list,
    print_error,
    print_warning,
    print_success,
    print_info,
)
from openai_edition.utils.formatter import format_history_datetime

console = Console(highlight=False)


@click.command("airline")
@click.argument("iata_code")
@click.option("--flights", "-f", is_flag=True, default=False,
              help="Show active flights for this airline.")
@click.option("--limit", "-l", default=10, show_default=True,
              help="Max number of flights to list.")
def airline_cmd(iata_code: str, flights: bool, limit: int) -> None:
    """
    Fetch airline information by IATA code.

    \b
    Examples:
      aero-openai airline LH
      aero-openai airline LH --flights
      aero-openai airline LH --flights --limit 20
    """
    iata_code = iata_code.upper().strip()
    raw = click.get_current_context().find_root().params.get("raw", False)
    client = AviationStackClient(raw=raw)

    try:
        airline = client.get_airline(iata_code)
    except AviationStackError as e:
        print_error(str(e))
        history_add("airline", iata_code, "api error")
        return

    if not airline:
        print_warning(f"Airline {iata_code} not found.")
        history_add("airline", iata_code, "not found")
        return

    print_airline(airline)
    history_add("airline", iata_code, "found")

    if flights:
        try:
            active_flights = client.get_flights_by_airline(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            return

        print_flights_list(active_flights, title=f"FLIGHTS  {iata_code}")


@click.command("airline-cache")
@click.option("--clear", "-c", is_flag=True, default=False,
              help="Clear the airline cache.")
def airline_cache_cmd(clear: bool) -> None:
    """
    View and manage the airline cache.

    \b
    Examples:
      aero-openai airline-cache
      aero-openai airline-cache --clear
    """
    if clear:
        deleted = airline_cache_clear()
        if deleted:
            print_success(f"Cache cleared. Removed {deleted} entries.")
        else:
            print_info("Cache is already empty.")
        return

    items = airline_cache_get_all()

    if not items:
        print_info("Cache is empty. Airlines are cached automatically on first lookup.")
        return

    table = Table(
        title=f"AIRLINE CACHE  ({len(items)} entries)",
        box=box.SIMPLE_HEAD,
        border_style="default",
        header_style="bold",
    )
    table.add_column("IATA",    style="bold", width=6)
    table.add_column("NAME",    style="default", min_width=24)
    table.add_column("COUNTRY", style="dim",  min_width=16)
    table.add_column("CACHED",  style="dim",  min_width=16)

    for item in items:
        data = airline_cache_get(item["iata_code"]) or {}
        table.add_row(
            item["iata_code"],
            data.get("airline_name") or "-",
            data.get("country_name") or "-",
            format_history_datetime(item["cached_at"]),
        )

    console.print(table)
