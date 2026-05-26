import click
from rich.console import Console

from openai_edition.db.database import init_db
from openai_edition.commands.flight import flight_cmd
from openai_edition.commands.airport import airport_cmd
from openai_edition.commands.airline import airline_cmd, airline_cache_cmd
from openai_edition.commands.watch import watch_cmd
from openai_edition.commands.history import history_cmd, stats_cmd

console = Console(highlight=False)

BANNER = """\
  AeroTrack  --  openai edition
  Flight tracking CLI
  ----------------------------------------
  commands: flight  airport  airline
            watch   history  stats
  ----------------------------------------\
"""


def print_banner() -> None:
    console.print(f"\n[dim]{BANNER}[/dim]\n")


@click.group()
@click.version_option(version="1.0.0", prog_name="aero-openai")
@click.option(
    "--raw",
    is_flag=True,
    default=False,
    help="Print full HTTP request and response.",
)
@click.pass_context
def cli(ctx: click.Context, raw: bool) -> None:
    """
    \b
    aero-openai  --  AeroTrack CLI, openai edition
    Minimal flight tracking tool for the terminal.

    \b
    Commands:
      flight        Flight status by IATA number
      airport       Airport information
      airline       Airline information
      watch         Manage watchlist (add / remove / list)
      history       Request history
      stats         Usage statistics
      airline-cache Manage airline cache

    \b
    Examples:
      aero-openai flight LH438
      aero-openai airport FRA --arrivals
      aero-openai airline LH --flights
      aero-openai watch add LH438
      aero-openai history
      aero-openai stats
      aero-openai --raw flight LH438
    """
    init_db()

    if raw:
        import openai_edition.api.aviationstack as av
        av.RAW_MODE = True

    if ctx.invoked_subcommand is None:
        print_banner()


cli.add_command(flight_cmd)
cli.add_command(airport_cmd)
cli.add_command(airline_cmd)
cli.add_command(airline_cache_cmd)
cli.add_command(watch_cmd)
cli.add_command(history_cmd)
cli.add_command(stats_cmd)


if __name__ == "__main__":
    cli()
