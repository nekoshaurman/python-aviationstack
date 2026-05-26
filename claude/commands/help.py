import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()


@click.command("help")
def help_cmd() -> None:
    """
    Памятка по всем доступным командам.
    """

    console.print()

    # Заголовок
    title = Text()
    title.append("✈  AeroTrack CLI", style="bold cyan")
    title.append("  —  памятка по командам", style="dim")
    console.print(Panel(title, border_style="cyan", expand=False))

    console.print()

    # ------------------------------------------------------------------ #
    #  Рейсы                                                               #
    # ------------------------------------------------------------------ #

    flights_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        expand=False,
    )
    flights_table.add_column("Команда",     style="bold white", min_width=42)
    flights_table.add_column("Описание",    style="white")
    flights_table.add_column("План",        style="dim", justify="center")

    flights_table.add_row(
        "aero-claude flight [cyan]<номер>[/cyan]",
        "Статус рейса",
        "✅ free",
    )
    flights_table.add_row(
        "aero-claude flight [cyan]<номер>[/cyan] --watch",
        "Следить за рейсом каждые 60 сек",
        "✅ free",
    )

    console.print(Panel(
        flights_table,
        title="[bold cyan]✈  Рейсы[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    console.print()

    # ------------------------------------------------------------------ #
    #  Аэропорты                                                           #
    # ------------------------------------------------------------------ #

    airport_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        expand=False,
    )
    airport_table.add_column("Команда",     style="bold white", min_width=42)
    airport_table.add_column("Описание",    style="white")
    airport_table.add_column("План",        style="dim", justify="center")

    airport_table.add_row(
        "aero-claude airport [cyan]<IATA>[/cyan]",
        "Карточка аэропорта",
        "❌ basic+",
    )
    airport_table.add_row(
        "aero-claude airport [cyan]<IATA>[/cyan] --arrivals",
        "Прилёты в аэропорт",
        "✅ free",
    )
    airport_table.add_row(
        "aero-claude airport [cyan]<IATA>[/cyan] --departures",
        "Вылеты из аэропорта",
        "✅ free",
    )
    airport_table.add_row(
        "aero-claude airport [cyan]<IATA>[/cyan] --arrivals --limit [cyan]<N>[/cyan]",
        "Прилёты, N рейсов",
        "✅ free",
    )

    console.print(Panel(
        airport_table,
        title="[bold cyan]🏢  Аэропорты[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    console.print()

    # ------------------------------------------------------------------ #
    #  Авиакомпании                                                        #
    # ------------------------------------------------------------------ #

    airline_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        expand=False,
    )
    airline_table.add_column("Команда",     style="bold white", min_width=42)
    airline_table.add_column("Описание",    style="white")
    airline_table.add_column("План",        style="dim", justify="center")

    airline_table.add_row(
        "aero-claude airline [cyan]<IATA>[/cyan]",
        "Карточка авиакомпании",
        "❌ basic+",
    )
    airline_table.add_row(
        "aero-claude airline [cyan]<IATA>[/cyan] --flights",
        "Активные рейсы авиакомпании",
        "✅ free",
    )
    airline_table.add_row(
        "aero-claude airline [cyan]<IATA>[/cyan] --flights --limit [cyan]<N>[/cyan]",
        "Активные рейсы, N штук",
        "✅ free",
    )

    console.print(Panel(
        airline_table,
        title="[bold cyan]🏷  Авиакомпании[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    console.print()

    # ------------------------------------------------------------------ #
    #  Watchlist                                                           #
    # ------------------------------------------------------------------ #

    watch_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        expand=False,
    )
    watch_table.add_column("Команда",     style="bold white", min_width=42)
    watch_table.add_column("Описание",    style="white")
    watch_table.add_column("План",        style="dim", justify="center")

    watch_table.add_row(
        "aero-claude watch add [cyan]<номер>[/cyan]",
        "Добавить рейс в watchlist",
        "💾 local",
    )
    watch_table.add_row(
        "aero-claude watch remove [cyan]<номер>[/cyan]",
        "Удалить рейс из watchlist",
        "💾 local",
    )
    watch_table.add_row(
        "aero-claude watch list",
        "Показать все рейсы в watchlist",
        "💾 local",
    )
    watch_table.add_row(
        "aero-claude watch clear",
        "Очистить весь watchlist",
        "💾 local",
    )

    console.print(Panel(
        watch_table,
        title="[bold cyan]📋  Watchlist[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    console.print()

    # ------------------------------------------------------------------ #
    #  История и статистика                                                #
    # ------------------------------------------------------------------ #

    history_table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
        padding=(0, 2),
        expand=False,
    )
    history_table.add_column("Команда",     style="bold white", min_width=42)
    history_table.add_column("Описание",    style="white")
    history_table.add_column("План",        style="dim", justify="center")

    history_table.add_row(
        "aero-claude history",
        "История всех запросов",
        "💾 local",
    )
    history_table.add_row(
        "aero-claude history --limit [cyan]<N>[/cyan]",
        "История, последние N записей",
        "💾 local",
    )
    history_table.add_row(
        "aero-claude history --clear",
        "Очистить историю",
        "💾 local",
    )
    history_table.add_row(
        "aero-claude stats",
        "Статистика использования",
        "💾 local",
    )

    console.print(Panel(
        history_table,
        title="[bold cyan]📜  История и статистика[/bold cyan]",
        border_style="cyan",
        expand=False,
    ))

    console.print()

    # Легенда
    legend = (
        "[dim]"
        "✅ free  — доступно на бесплатном плане    "
        "❌ basic+  — требует платный план    "
        "💾 local  — работает без API"
        "[/dim]"
    )
    console.print(legend)
    console.print()