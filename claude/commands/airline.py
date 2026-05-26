import click
from rich.console import Console
from rich.table import Table
from rich import box

from claude.api.aviationstack import AviationStackClient, AviationStackError
from claude.db.database import (
    history_add,
    airline_cache_get_all,
    airline_cache_clear,
    airline_cache_get,
)
from claude.utils.display import (
    print_airline,
    print_flights_list,
    print_error,
    print_warning,
    print_success,
    print_info,
)
from claude.utils.formatter import format_history_datetime

console = Console()


@click.command("airline")
@click.argument("iata_code")
@click.option("--flights", "-f", is_flag=True, default=False,
              help="Показать активные рейсы авиакомпании.")
@click.option("--limit", "-l", default=10, show_default=True,
              help="Количество рейсов в списке.")
def airline_cmd(iata_code: str, flights: bool, limit: int) -> None:
    """
    Информация об авиакомпании по коду IATA.

    \b
    Примеры:
      aero-claude airline LH
      aero-claude airline LH --flights
      aero-claude airline LH --flights --limit 20
    """
    iata_code = iata_code.upper().strip()
    raw = click.get_current_context().find_root().params.get("raw", False)
    client = AviationStackClient(raw=raw)

    try:
        airline = client.get_airline(iata_code)
    except AviationStackError as e:
        print_error(str(e))
        history_add("airline", iata_code, "Ошибка API")
        return

    if not airline:
        print_warning(f"Авиакомпания [bold]{iata_code}[/bold] не найдена.")
        history_add("airline", iata_code, "Не найдена")
        return

    print_airline(airline)
    history_add("airline", iata_code, "Найдена")

    if flights:
        try:
            active_flights = client.get_flights_by_airline(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            return

        print_flights_list(active_flights, title=f"✈  Активные рейсы  {iata_code}")


@click.command("airline-cache")
@click.option("--clear", "-c", is_flag=True, default=False,
              help="Очистить кеш авиакомпаний.")
def airline_cache_cmd(clear: bool) -> None:
    """
    Просмотр и управление кешем авиакомпаний.

    \b
    Примеры:
      aero-claude airline-cache
      aero-claude airline-cache --clear
    """
    if clear:
        deleted = airline_cache_clear()
        if deleted:
            print_success(f"Кеш очищен. Удалено записей: {deleted}.")
        else:
            print_info("Кеш уже пуст.")
        return

    items = airline_cache_get_all()

    if not items:
        print_info("Кеш пуст. Авиакомпании сохраняются автоматически при запросе.")
        return

    table = Table(
        title=f"💾  Кеш авиакомпаний  ({len(items)} записей)",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )
    table.add_column("IATA",         style="bold white", width=6)
    table.add_column("Название",     style="white",      min_width=24)
    table.add_column("Страна",       style="dim",        min_width=16)
    table.add_column("Закешировано", style="dim",        min_width=16)

    for item in items:
        data = airline_cache_get(item["iata_code"]) or {}
        table.add_row(
            item["iata_code"],
            data.get("airline_name") or "—",
            data.get("country_name") or "—",
            format_history_datetime(item["cached_at"]),
        )

    console.print(table)