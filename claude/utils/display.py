from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from claude.utils.formatter import (
    format_flight,
    format_airport,
    format_airline,
    format_history_datetime,
    truncate,
)

console = Console()


# ------------------------------------------------------------------ #
#  Вспомогательные функции                                             #
# ------------------------------------------------------------------ #

def _row(label: str, value: str) -> tuple[str, str]:
    """Строка для двухколоночной таблицы."""
    return f"[dim]{label}[/dim]", value or "—"


def print_error(message: str) -> None:
    """Вывести сообщение об ошибке."""
    console.print(f"\n[bold red]✖  {message}[/bold red]\n")


def print_success(message: str) -> None:
    """Вывести сообщение об успехе."""
    console.print(f"\n[bold green]✔  {message}[/bold green]\n")


def print_warning(message: str) -> None:
    """Вывести предупреждение."""
    console.print(f"\n[bold yellow]⚠  {message}[/bold yellow]\n")


def print_info(message: str) -> None:
    """Вывести информационное сообщение."""
    console.print(f"\n[bold cyan]ℹ  {message}[/bold cyan]\n")


# ------------------------------------------------------------------ #
#  Рейс                                                                #
# ------------------------------------------------------------------ #

def print_flight(raw: dict) -> None:
    """
    Вывести карточку рейса.

    ╭─────────────────────────────────────────╮
    │  ✈  Aeroflot  SU100                     │
    ╰─────────────────────────────────────────╯
    """
    f = format_flight(raw)

    title = Text()
    title.append("✈  ", style="bold cyan")
    title.append(f["airline_name"], style="bold white")
    title.append(f"  {f['flight_iata']}", style="bold cyan")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=18)
    table.add_column(style="white")

    table.add_row("Статус",     f["status"])
    table.add_row("Авиакомпания", f"{f['airline_name']} ({f['airline_iata']})")
    table.add_section()
    table.add_row("Откуда",     f"{f['dep_airport']} [cyan]({f['dep_iata']})[/cyan]")
    table.add_row("Вылет",      f"{f['dep_scheduled']}"
                                + (f"  →  факт [green]{f['dep_actual']}[/green]"
                                   if f["dep_actual"] != "—" else ""))
    table.add_row("Задержка вылета", f["dep_delay"])
    table.add_row("Терминал / гейт",
                  f"{f['dep_terminal']} / {f['dep_gate']}")
    table.add_section()
    table.add_row("Куда",       f"{f['arr_airport']} [cyan]({f['arr_iata']})[/cyan]")
    table.add_row("Прилёт",     f"{f['arr_scheduled']}"
                                + (f"  →  факт [green]{f['arr_actual']}[/green]"
                                   if f["arr_actual"] != "—" else ""))
    table.add_row("Ожидается",  f["arr_estimated"])
    table.add_row("Задержка прилёта", f["arr_delay"])
    table.add_row("Терминал / гейт",
                  f"{f['arr_terminal']} / {f['arr_gate']}")
    table.add_section()
    table.add_row("Борт",       f"{f['aircraft_reg']} ({f['aircraft_type']})")

    # Live данные — только если рейс в воздухе
    if not f["is_grounded"] and f["altitude"] != "—":
        table.add_section()
        table.add_row("Высота",   f["altitude"])
        table.add_row("Скорость", f["speed"])

    console.print(Panel(table, title=title, border_style="cyan", expand=False))


def print_flights_list(flights: list[dict], title: str = "Рейсы") -> None:
    """
    Вывести список рейсов в виде таблицы.
    Используется для прилётов, вылетов, рейсов авиакомпании.
    """
    if not flights:
        print_warning("Рейсы не найдены.")
        return

    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=False,
    )

    table.add_column("Рейс",       style="bold white", min_width=8)
    table.add_column("Авиакомпания", style="white",    min_width=16)
    table.add_column("Откуда",     style="cyan",       min_width=6)
    table.add_column("Куда",       style="cyan",       min_width=6)
    table.add_column("Вылет",      style="white",      min_width=6)
    table.add_column("Прилёт",     style="white",      min_width=6)
    table.add_column("Статус",     min_width=16)

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
#  Аэропорт                                                            #
# ------------------------------------------------------------------ #

def print_airport(raw: dict) -> None:
    """
    Вывести карточку аэропорта.
    """
    a = format_airport(raw)

    title = Text()
    title.append("🏢  ", style="bold cyan")
    title.append(a["name"], style="bold white")
    title.append(f"  {a['iata']}", style="bold cyan")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=14)
    table.add_column(style="white")

    table.add_row("IATA / ICAO", f"{a['iata']} / {a['icao']}")
    table.add_row("Город",       a["city"])
    table.add_row("Страна",      f"{a['country']} ({a['country_iso']})")
    table.add_row("Часовой пояс", a["timezone"])
    table.add_row("Координаты",  f"{a['latitude']}, {a['longitude']}")
    if a["phone"] != "—":
        table.add_row("Телефон", a["phone"])

    console.print(Panel(table, title=title, border_style="cyan", expand=False))


# ------------------------------------------------------------------ #
#  Авиакомпания                                                        #
# ------------------------------------------------------------------ #

def print_airline(raw: dict) -> None:
    """
    Вывести карточку авиакомпании.
    """
    a = format_airline(raw)

    title = Text()
    title.append("🏷  ", style="bold cyan")
    title.append(a["name"], style="bold white")
    title.append(f"  {a['iata']}", style="bold cyan")

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
        expand=False,
    )
    table.add_column(style="dim", min_width=16)
    table.add_column(style="white")

    table.add_row("IATA / ICAO",  f"{a['iata']} / {a['icao']}")
    table.add_row("Позывной",     a["callsign"])
    table.add_row("Страна",       f"{a['country']} ({a['country_iso']})")
    table.add_row("Хаб",          a["hub"])
    table.add_row("Статус",       a["status"])
    table.add_row("Основана",     a["founded"])
    table.add_row("Флот",         f"{a['fleet_size']} самолётов")
    table.add_row("Средний возраст флота", f"{a['fleet_avg_age']} лет")

    console.print(Panel(table, title=title, border_style="cyan", expand=False))


# ------------------------------------------------------------------ #
#  Watchlist                                                           #
# ------------------------------------------------------------------ #

def print_watchlist(items: list[dict]) -> None:
    """
    Вывести список отслеживаемых рейсов.
    """
    if not items:
        print_info("Watchlist пуст. Добавь рейс: watch add <номер>")
        return

    table = Table(
        title="📋  Watchlist",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )

    table.add_column("№",          style="dim",        width=4)
    table.add_column("Рейс",       style="bold white", min_width=10)
    table.add_column("Добавлен",   style="white",      min_width=16)

    for i, item in enumerate(items, 1):
        table.add_row(
            str(i),
            item["flight_iata"],
            format_history_datetime(item["added_at"]),
        )

    console.print(table)


# ------------------------------------------------------------------ #
#  История                                                             #
# ------------------------------------------------------------------ #

def print_history(records: list[dict]) -> None:
    """
    Вывести историю запросов.
    """
    if not records:
        print_info("История пуста.")
        return

    table = Table(
        title="📜  История запросов",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
    )

    table.add_column("Время",    style="dim",        min_width=16)
    table.add_column("Команда",  style="bold cyan",  min_width=10)
    table.add_column("Запрос",   style="bold white", min_width=10)
    table.add_column("Результат", style="white",     min_width=16)

    for rec in records:
        table.add_row(
            format_history_datetime(rec["requested_at"]),
            rec["command"],
            rec["query"],
            rec.get("result") or "—",
        )

    console.print(table)


# ------------------------------------------------------------------ #
#  Статистика                                                          #
# ------------------------------------------------------------------ #

def print_stats(stats: dict) -> None:
    """
    Вывести статистику использования приложения.
    """
    # Основная панель
    main_table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
    )
    main_table.add_column(style="dim", min_width=22)
    main_table.add_column(style="bold white")

    main_table.add_row("Всего запросов",       str(stats["total_requests"]))
    main_table.add_row("Рейсов в watchlist",   str(stats["watchlist_count"]))
    main_table.add_row("Первый запрос",
                       format_history_datetime(stats["first_request"]))
    main_table.add_row("Последний запрос",
                       format_history_datetime(stats["last_request"]))

    console.print(Panel(
        main_table,
        title="[bold cyan]📊  Статистика[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    # Запросы по командам
    if stats["by_command"]:
        cmd_table = Table(
            title="По командам",
            box=box.SIMPLE,
            header_style="bold cyan",
            padding=(0, 2),
        )
        cmd_table.add_column("Команда", style="cyan")
        cmd_table.add_column("Запросов", style="bold white", justify="right")

        for cmd, count in stats["by_command"].items():
            cmd_table.add_row(cmd, str(count))

        console.print(cmd_table)

    # Топ запросы
    if stats["top_queries"]:
        top_table = Table(
            title="Топ запросов",
            box=box.SIMPLE,
            header_style="bold cyan",
            padding=(0, 2),
        )
        top_table.add_column("Запрос",   style="bold white")
        top_table.add_column("Раз",      style="dim", justify="right")

        for item in stats["top_queries"]:
            top_table.add_row(item["query"], str(item["count"]))

        console.print(top_table)