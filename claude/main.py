import click
from rich.console import Console
from rich.text import Text

from claude.db.database import init_db
from claude.commands.flight import flight_cmd
from claude.commands.airport import airport_cmd
from claude.commands.airline import airline_cmd, airline_cache_cmd
from claude.commands.watch import watch_cmd
from claude.commands.history import history_cmd, stats_cmd
from claude.commands.help import help_cmd

console = Console()

BANNER = """
[bold cyan]  ✈   AeroTrack CLI[/bold cyan]  [dim]claude edition[/dim]
[dim]  Персональный авиационный помощник[/dim]
"""


def print_banner() -> None:
    console.print(BANNER)


@click.group()
@click.version_option(version="1.0.0", prog_name="AeroTrack CLI — claude")
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help="Показать полный HTTP запрос и ответ API.",
)
@click.pass_context
def cli(ctx: click.Context, raw: bool) -> None:
    """
    \b
    ✈  AeroTrack CLI — claude edition
    Персональный авиационный помощник.

    \b
    Команды:
      flight    Статус рейса
      airport   Информация об аэропорте
      airline   Информация об авиакомпании
      watch     Управление watchlist
      history   История запросов
      stats     Статистика
      help      Памятка по командам

    \b
    Примеры:
      aero-claude flight LH438
      aero-claude airport FRA --arrivals
      aero-claude airline LH --flights
      aero-claude watch add LH438
      aero-claude history
      aero-claude stats
      aero-claude --raw flight LH438
    """
    init_db()

    # Включаем RAW_MODE глобально если передан флаг
    if raw:
        import claude.api.aviationstack as av
        av.RAW_MODE = True

    if ctx.invoked_subcommand is None:
        print_banner()


# Регистрация команд
cli.add_command(flight_cmd)
cli.add_command(airport_cmd)
cli.add_command(airline_cmd)
cli.add_command(airline_cache_cmd)
cli.add_command(watch_cmd)
cli.add_command(history_cmd)
cli.add_command(stats_cmd)
cli.add_command(help_cmd)


if __name__ == "__main__":
    cli()