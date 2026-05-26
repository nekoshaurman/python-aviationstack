import click
from click.testing import CliRunner

from openai_edition.db import database
from openai_edition.main import cli


def test_cli_flight_positive_scenario(monkeypatch):
    from openai_edition.commands import flight as flight_module

    class FakeClient:
        def __init__(self, raw=False):
            self.raw = raw

        def get_flight(self, flight_iata):
            return {
                "flight_status": "active",
                "flight": {"iata": flight_iata},
                "airline": {"name": "Test Airline", "iata": "TA"},
                "departure": {"airport": "A", "iata": "AAA"},
                "arrival": {"airport": "B", "iata": "BBB"},
            }

    monkeypatch.setattr(flight_module, "AviationStackClient", FakeClient)
    monkeypatch.setattr(flight_module, "print_flight", lambda raw: None)

    runner = CliRunner()
    result = runner.invoke(cli, ["flight", "su100"])

    assert result.exit_code == 0

    history = database.history_get_all(limit=5)
    assert len(history) == 1
    assert history[0]["command"] == "flight"
    assert history[0]["query"] == "SU100"
    assert history[0]["result"] == "active"


def test_cli_watch_add_list_remove_scenario():
    runner = CliRunner()

    add_result = runner.invoke(cli, ["watch", "add", "su100"])
    assert add_result.exit_code == 0
    assert database.watchlist_exists("SU100") is True

    list_result = runner.invoke(cli, ["watch", "list"])
    assert list_result.exit_code == 0
    assert "SU100" in list_result.output

    remove_result = runner.invoke(cli, ["watch", "remove", "su100"])
    assert remove_result.exit_code == 0
    assert database.watchlist_exists("SU100") is False


def test_cli_history_basic_scenario(monkeypatch):
    from openai_edition.commands import history as history_module

    database.history_add("flight", "su100", "active")
    database.history_add("airport", "fra", "found")

    monkeypatch.setattr(
        history_module,
        "print_history",
        lambda records: click.echo(f"history_records={len(records)}"),
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["history", "--limit", "10"])

    assert result.exit_code == 0
    assert "history_records=2" in result.output


def test_cli_stats_empty_and_non_empty_scenarios(monkeypatch):
    from openai_edition.commands import history as history_module

    monkeypatch.setattr(history_module, "print_info", lambda msg: click.echo(f"INFO:{msg}"))
    monkeypatch.setattr(
        history_module,
        "print_stats",
        lambda stats: click.echo(f"STATS:{stats['total_requests']}"),
    )

    runner = CliRunner()
    empty_result = runner.invoke(cli, ["stats"])
    assert empty_result.exit_code == 0
    assert "INFO:No requests recorded yet." in empty_result.output

    database.history_add("flight", "su100", "active")
    non_empty_result = runner.invoke(cli, ["stats"])
    assert non_empty_result.exit_code == 0
    assert "STATS:1" in non_empty_result.output

