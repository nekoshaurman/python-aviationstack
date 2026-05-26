import click

from claude.api.aviationstack import AviationStackClient, AviationStackError
from claude.db.database import history_add
from claude.utils.display import (
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
    help="Показать прилёты в аэропорт.",
)
@click.option(
    "--departures", "-d",
    is_flag=True,
    default=False,
    help="Показать вылеты из аэропорта.",
)
@click.option(
    "--limit", "-l",
    default=10,
    show_default=True,
    help="Количество рейсов в списке.",
)
def airport_cmd(iata_code: str, arrivals: bool, departures: bool, limit: int) -> None:
    """
    Информация об аэропорте по коду IATA.

    \b
    Примеры:
      aero airport FRA
      aero airport JFK --arrivals
      aero airport SVO --departures --limit 20
    """
    iata_code = iata_code.upper().strip()
    client = AviationStackClient()

    # Без флагов — показать карточку аэропорта
    if not arrivals and not departures:
        try:
            airport = client.get_airport(iata_code)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "Ошибка API")
            return

        if not airport:
            print_warning(f"Аэропорт [bold]{iata_code}[/bold] не найден.")
            history_add("airport", iata_code, "Не найден")
            return

        print_airport(airport)
        history_add("airport", iata_code, "Найден")
        return

    # Флаг --arrivals
    if arrivals:
        try:
            flights = client.get_arrivals(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "Ошибка API")
            return

        print_flights_list(flights, title=f"🛬  Прилёты  {iata_code}")
        history_add("airport", iata_code, f"Прилёты: {len(flights)}")

    # Флаг --departures
    if departures:
        try:
            flights = client.get_departures(iata_code, limit=limit)
        except AviationStackError as e:
            print_error(str(e))
            history_add("airport", iata_code, "Ошибка API")
            return

        print_flights_list(flights, title=f"🛫  Вылеты  {iata_code}")
        history_add("airport", iata_code, f"Вылеты: {len(flights)}")