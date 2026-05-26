import time
import click

from openai_edition.api.aviationstack import AviationStackClient, AviationStackError
from openai_edition.db.database import history_add
from openai_edition.utils.display import (
    console,
    print_flight,
    print_error,
    print_warning,
    print_info,
)


@click.command("flight")
@click.argument("flight_iata")
@click.option(
    "--watch", "-w",
    is_flag=True,
    default=False,
    help="Poll flight status every 60 seconds.",
)
def flight_cmd(flight_iata: str, watch: bool) -> None:
    """
    Fetch flight status by IATA number.

    \b
    Examples:
      aero-openai flight SU100
      aero-openai flight LH438 --watch
    """
    flight_iata = flight_iata.upper().strip()
    raw = click.get_current_context().find_root().params.get("raw", False)
    client = AviationStackClient(raw=raw)

    def fetch_and_display() -> bool:
        try:
            flight = client.get_flight(flight_iata)
        except AviationStackError as e:
            print_error(str(e))
            return False

        if not flight:
            print_warning(f"Flight {flight_iata} not found.")
            history_add("flight", flight_iata, "not found")
            return False

        status = flight.get("flight_status", "-")
        print_flight(flight)
        history_add("flight", flight_iata, status)
        return True

    if not watch:
        fetch_and_display()
        return

    print_info(f"Watching flight {flight_iata}. Press Ctrl+C to stop.")

    try:
        while True:
            console.rule("[dim]update[/dim]")
            fetch_and_display()
            time.sleep(60)
    except KeyboardInterrupt:
        print_info("Watch stopped.")
