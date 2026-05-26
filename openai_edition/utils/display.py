from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from openai_edition.utils.formatter import (
    format_flight,
    format_airport,
    format_airline,
    format_history_datetime,
    truncate,
)

console = Console(highlight=False)

# Monochrome box style — plain ASCII, no color borders
_BOX = box.SIMPLE_HEAD


# ------------------------------------------------------------------ #
#  Status messages                                                     #
# ------------------------------------------------------------------ #

def print_error(message: str) -> None:
    console.print(f"\n[bold]ERROR[/bold]  {message}\n")


def print_success(message: str) -> None:
    console.print(f"\nOK  {message}\n")


def print_warning(message: str) -> None:
    console.print(f"\nWARN  {message}\n")


def print_info(message: str) -> None:
    console.print(f"\nINFO  {message}\n")


# ------------------------------------------------------------------ #
#  Flight                                                              #
# ------------------------------------------------------------------ #

def print_flight(raw: dict) -> None:
    """
    Render a flight card.

    FLIGHT  LH438  Lufthansa
    --------------------------------
    STATUS     [ON TIME]
    ...
    """
    f = format_flight(raw)

    title = Text()
    title.append("FLIGHT  ", style="bold")
    title.append(f["flight_iata"], style="bold")
    title.append(f"  {f['airline_name']}", style="dim")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=18)
    table.add_column(style="default")

    table.add_row("STATUS",   f["status"])
    table.add_row("AIRLINE",  f"{f['airline_name']} ({f['airline_iata']})")
    table.add_section()
    table.add_row("FROM",     f"{f['dep_airport']} ({f['dep_iata']})")

    dep_time = f["dep_scheduled"]
    if f["dep_actual"] != "-":
        dep_time += f"  actual {f['dep_actual']}"
    table.add_row("DEPARTS",  dep_time)
    table.add_row("DEP DELAY", f["dep_delay"])
    table.add_row("TERMINAL / GATE", f"{f['dep_terminal']} / {f['dep_gate']}")

    table.add_section()
    table.add_row("TO",       f"{f['arr_airport']} ({f['arr_iata']})")

    arr_time = f["arr_scheduled"]
    if f["arr_actual"] != "-":
        arr_time += f"  actual {f['arr_actual']}"
    table.add_row("ARRIVES",  arr_time)
    table.add_row("ESTIMATED", f["arr_estimated"])
    table.add_row("ARR DELAY", f["arr_delay"])
    table.add_row("TERMINAL / GATE", f"{f['arr_terminal']} / {f['arr_gate']}")

    table.add_section()
    table.add_row("AIRCRAFT", f"{f['aircraft_reg']} ({f['aircraft_type']})")

    if not f["is_grounded"] and f["altitude"] != "-":
        table.add_section()
        table.add_row("ALTITUDE", f["altitude"])
        table.add_row("SPEED",    f["speed"])

    console.print(Panel(table, title=title, border_style="default", expand=False))


def print_flights_list(flights: list[dict], title: str = "FLIGHTS") -> None:
    """Render a tabular list of flights."""
    if not flights:
        print_warning("No flights found.")
        return

    table = Table(
        title=title,
        box=_BOX,
        border_style="default",
        header_style="bold",
        show_lines=False,
    )

    table.add_column("FLIGHT",   style="bold", min_width=8)
    table.add_column("AIRLINE",  style="default", min_width=16)
    table.add_column("FROM",     style="dim",  min_width=6)
    table.add_column("TO",       style="dim",  min_width=6)
    table.add_column("DEP",      style="default", min_width=6)
    table.add_column("ARR",      style="default", min_width=6)
    table.add_column("STATUS",   min_width=12)

    for raw in flights:
        f = format_flight(raw)
        table.add_row(
            f["flight_iata"],
            truncate(f["airline_name"], 20),
            f["dep_iata"],
            f["arr_iata"],
            f["dep_scheduled"],
            f["arr_scheduled"],
            f["status"],
        )

    console.print(table)


# ------------------------------------------------------------------ #
#  Airport                                                             #
# ------------------------------------------------------------------ #

def print_airport(raw: dict) -> None:
    """Render an airport info card."""
    a = format_airport(raw)

    title = Text()
    title.append("AIRPORT  ", style="bold")
    title.append(a["iata"], style="bold")
    title.append(f"  {a['name']}", style="dim")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=14)
    table.add_column(style="default")

    table.add_row("IATA / ICAO", f"{a['iata']} / {a['icao']}")
    table.add_row("CITY",       a["city"])
    table.add_row("COUNTRY",    f"{a['country']} ({a['country_iso']})")
    table.add_row("TIMEZONE",   a["timezone"])
    table.add_row("COORDS",     f"{a['latitude']}, {a['longitude']}")
    if a["phone"] != "-":
        table.add_row("PHONE", a["phone"])

    console.print(Panel(table, title=title, border_style="default", expand=False))


# ------------------------------------------------------------------ #
#  Airline                                                             #
# ------------------------------------------------------------------ #

def print_airline(raw: dict) -> None:
    """Render an airline info card."""
    a = format_airline(raw)

    title = Text()
    title.append("AIRLINE  ", style="bold")
    title.append(a["iata"], style="bold")
    title.append(f"  {a['name']}", style="dim")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=16)
    table.add_column(style="default")

    table.add_row("IATA / ICAO",    f"{a['iata']} / {a['icao']}")
    table.add_row("CALLSIGN",       a["callsign"])
    table.add_row("COUNTRY",        f"{a['country']} ({a['country_iso']})")
    table.add_row("HUB",            a["hub"])
    table.add_row("STATUS",         a["status"])
    table.add_row("FOUNDED",        a["founded"])
    table.add_row("FLEET SIZE",     f"{a['fleet_size']} aircraft")
    table.add_row("AVG FLEET AGE",  f"{a['fleet_avg_age']} years")

    console.print(Panel(table, title=title, border_style="default", expand=False))


# ------------------------------------------------------------------ #
#  Watchlist                                                           #
# ------------------------------------------------------------------ #

def print_watchlist(items: list[dict]) -> None:
    """Render the watchlist table."""
    if not items:
        print_info("Watchlist is empty.  Use: watch add <IATA>")
        return

    table = Table(
        title=f"WATCHLIST  ({len(items)} flights)",
        box=_BOX,
        border_style="default",
        header_style="bold",
    )

    table.add_column("#",       style="dim",  width=4)
    table.add_column("FLIGHT",  style="bold", min_width=10)
    table.add_column("ADDED",   style="dim",  min_width=16)

    for i, item in enumerate(items, 1):
        table.add_row(
            str(i),
            item["flight_iata"],
            format_history_datetime(item["added_at"]),
        )

    console.print(table)


# ------------------------------------------------------------------ #
#  History                                                             #
# ------------------------------------------------------------------ #

def print_history(records: list[dict]) -> None:
    """Render the request history table."""
    if not records:
        print_info("History is empty.")
        return

    table = Table(
        title=f"HISTORY  ({len(records)} records)",
        box=_BOX,
        border_style="default",
        header_style="bold",
    )

    table.add_column("TIME",    style="dim",  min_width=16)
    table.add_column("CMD",     style="bold", min_width=10)
    table.add_column("QUERY",   style="bold", min_width=10)
    table.add_column("RESULT",  style="dim",  min_width=16)

    for rec in records:
        table.add_row(
            format_history_datetime(rec["requested_at"]),
            rec["command"],
            rec["query"],
            rec.get("result") or "-",
        )

    console.print(table)


# ------------------------------------------------------------------ #
#  Stats                                                               #
# ------------------------------------------------------------------ #

def print_stats(stats: dict) -> None:
    """Render usage statistics."""
    main_table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
    )
    main_table.add_column(style="dim", min_width=22)
    main_table.add_column(style="bold")

    main_table.add_row("total requests",    str(stats["total_requests"]))
    main_table.add_row("flights in watchlist", str(stats["watchlist_count"]))
    main_table.add_row("first request",     format_history_datetime(stats["first_request"]))
    main_table.add_row("last request",      format_history_datetime(stats["last_request"]))

    console.print(Panel(
        main_table,
        title="[bold]STATS[/bold]",
        border_style="default",
        expand=False,
    ))

    if stats["by_command"]:
        cmd_table = Table(
            title="by command",
            box=_BOX,
            header_style="bold",
            padding=(0, 2),
        )
        cmd_table.add_column("command", style="bold")
        cmd_table.add_column("count",   style="default", justify="right")

        for cmd, count in stats["by_command"].items():
            cmd_table.add_row(cmd, str(count))

        console.print(cmd_table)

    if stats["top_queries"]:
        top_table = Table(
            title="top queries",
            box=_BOX,
            header_style="bold",
            padding=(0, 2),
        )
        top_table.add_column("query", style="bold")
        top_table.add_column("times", style="dim", justify="right")

        for item in stats["top_queries"]:
            top_table.add_row(item["query"], str(item["count"]))

        console.print(top_table)
