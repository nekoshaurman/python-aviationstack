import time
import click

from claude.api.aviationstack import AviationStackClient, AviationStackError
from claude.db.database import history_add
from claude.utils.display import (
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
    help="Следить за рейсом, обновляя каждые 60 секунд.",
)
def flight_cmd(flight_iata: str, watch: bool) -> None:
    """
    Статус рейса по номеру IATA.

    \b
    Примеры:
      aero flight SU100
      aero flight LH438 --watch
    """
    flight_iata = flight_iata.upper().strip()
    raw = click.get_current_context().find_root().params.get("raw", False)
    client = AviationStackClient(raw=raw)

    def fetch_and_display() -> bool:
        """Получить и вывести рейс. Возвращает True если найден."""
        try:
            flight = client.get_flight(flight_iata)
        except AviationStackError as e:
            print_error(str(e))
            return False

        if not flight:
            print_warning(f"Рейс [bold]{flight_iata}[/bold] не найден.")
            history_add("flight", flight_iata, "Не найден")
            return False

        status = flight.get("flight_status", "—")
        print_flight(flight)
        history_add("flight", flight_iata, status)
        return True

    if not watch:
        fetch_and_display()
        return

    # Режим --watch
    print_info(f"Слежение за рейсом [bold]{flight_iata}[/bold]. Ctrl+C для остановки.")

    try:
        while True:
            console.rule(f"[dim]Обновление…[/dim]")
            fetch_and_display()
            time.sleep(60)
    except KeyboardInterrupt:
        print_info("Слежение остановлено.")