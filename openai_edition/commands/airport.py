import click

from openai_edition.api.aviationstack import AviationStackClient, AviationStackError
from openai_edition.db.database import history_add
from openai_edition.utils.display import (
    print_airport,
    print_flights_list,
    print_error,
    print_warning,
)


@click.command("airport")
@click.argument("iata_code")
@click.option(
    "--arrivals", "-a",
    is_flag=True,
    default=False,
    help="Show arrivals at this airport.",
)
@click.option(
    "--departures", "-d",
    is_flag=True,
    default=False,
    help="Show departures from this airport.",
)
@click.option(
    "--limit", "-l",
    default=10,
    show_default=True,
    help="Max number of flights to list.",
)
def airport_cmd(iata_code: str, arrivals: bool, departures: bool, limit: int) -> None:
    """
    Fetch airport information by IATA code.

    \b
    Examples:
      aero-openai airport FRA
      aero-openai airport JFK --arrivals
      aero-openai airport SVO --departures --limit 20
    """
    iata_code = iata_code.upper().strip()
    client = AviationStackClient()

    if not arrivals and not departures:
        try:
            airport = client.get_airport(iata_code)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "api error")
            return

        if not airport:
            print_warning(f"Airport {iata_code} not found.")
            history_add("airport", iata_code, "not found")
            return

        print_airport(airport)
        history_add("airport", iata_code, "found")
        return

    if arrivals:
        try:
            flights = client.get_arrivals(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "api error")
            return

        print_flights_list(flights, title=f"ARRIVALS  {iata_code}")
        history_add("airport", iata_code, f"arrivals: {len(flights)}")

    if departures:
        try:
            flights = client.get_departures(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "api error")
            return

        print_flights_list(flights, title=f"DEPARTURES  {iata_code}")
        history_add("airport", iata_code, f"departures: {len(flights)}")
