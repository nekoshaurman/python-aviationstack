import click

from openai_edition.db.database import (
    watchlist_add,
    watchlist_remove,
    watchlist_get_all,
    watchlist_exists,
)
from openai_edition.utils.display import (
    print_watchlist,
    print_success,
    print_error,
    print_warning,
    print_info,
)


@click.group("watch")
def watch_cmd() -> None:
    """
    Manage the flight watchlist.

    \b
    Examples:
      aero-openai watch add SU100
      aero-openai watch list
      aero-openai watch remove SU100
    """


@watch_cmd.command("add")
@click.argument("flight_iata")
def watch_add(flight_iata: str) -> None:
    """Add a flight to the watchlist."""
    flight_iata = flight_iata.upper().strip()

    if watchlist_exists(flight_iata):
        print_warning(f"Flight {flight_iata} is already in the watchlist.")
        return

    added = watchlist_add(flight_iata)
    if added:
        print_success(f"Flight {flight_iata} added to watchlist.")
    else:
        print_error(f"Failed to add flight {flight_iata}.")


@watch_cmd.command("remove")
@click.argument("flight_iata")
def watch_remove(flight_iata: str) -> None:
    """Remove a flight from the watchlist."""
    flight_iata = flight_iata.upper().strip()

    if not watchlist_exists(flight_iata):
        print_warning(f"Flight {flight_iata} is not in the watchlist.")
        return

    removed = watchlist_remove(flight_iata)
    if removed:
        print_success(f"Flight {flight_iata} removed from watchlist.")
    else:
        print_error(f"Failed to remove flight {flight_iata}.")


@watch_cmd.command("list")
def watch_list() -> None:
    """List all flights in the watchlist."""
    items = watchlist_get_all()
    print_watchlist(items)


@watch_cmd.command("clear")
@click.confirmation_option(prompt="Remove all flights from watchlist?")
def watch_clear() -> None:
    """Clear the entire watchlist."""
    items = watchlist_get_all()
    if not items:
        print_info("Watchlist is already empty.")
        return

    for item in items:
        watchlist_remove(item["flight_iata"])

    print_success(f"Watchlist cleared. Removed {len(items)} flights.")
