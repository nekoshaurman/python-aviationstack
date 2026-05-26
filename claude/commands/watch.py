import click

from claude.db.database import (
    watchlist_add,
    watchlist_remove,
    watchlist_get_all,
    watchlist_exists,
)
from claude.utils.display import (
    print_watchlist,
    print_success,
    print_error,
    print_warning,
    print_info,
)


@click.group("watch")
def watch_cmd() -> None:
    """
    Управление списком отслеживаемых рейсов.

    \b
    Примеры:
      aero watch add SU100
      aero watch list
      aero watch remove SU100
    """


@watch_cmd.command("add")
@click.argument("flight_iata")
def watch_add(flight_iata: str) -> None:
    """Добавить рейс в watchlist."""
    flight_iata = flight_iata.upper().strip()

    if watchlist_exists(flight_iata):
        print_warning(f"Рейс [bold]{flight_iata}[/bold] уже в watchlist.")
        return

    added = watchlist_add(flight_iata)
    if added:
        print_success(f"Рейс [bold]{flight_iata}[/bold] добавлен в watchlist.")
    else:
        print_error(f"Не удалось добавить рейс [bold]{flight_iata}[/bold].")


@watch_cmd.command("remove")
@click.argument("flight_iata")
def watch_remove(flight_iata: str) -> None:
    """Удалить рейс из watchlist."""
    flight_iata = flight_iata.upper().strip()

    if not watchlist_exists(flight_iata):
        print_warning(f"Рейс [bold]{flight_iata}[/bold] не найден в watchlist.")
        return

    removed = watchlist_remove(flight_iata)
    if removed:
        print_success(f"Рейс [bold]{flight_iata}[/bold] удалён из watchlist.")
    else:
        print_error(f"Не удалось удалить рейс [bold]{flight_iata}[/bold].")


@watch_cmd.command("list")
def watch_list() -> None:
    """Показать все рейсы в watchlist."""
    items = watchlist_get_all()
    print_watchlist(items)


@watch_cmd.command("clear")
@click.confirmation_option(
    prompt="Удалить все рейсы из watchlist?"
)
def watch_clear() -> None:
    """Очистить весь watchlist."""
    items = watchlist_get_all()
    if not items:
        print_info("Watchlist уже пуст.")
        return

    for item in items:
        watchlist_remove(item["flight_iata"])

    print_success(f"Watchlist очищен. Удалено рейсов: {len(items)}.")