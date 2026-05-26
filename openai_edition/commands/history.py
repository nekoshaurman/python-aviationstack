import click

from openai_edition.db.database import history_get_all, history_clear, get_stats
from openai_edition.utils.display import (
    print_history,
    print_stats,
    print_success,
    print_info,
)


@click.command("history")
@click.option(
    "--limit", "-l",
    default=50,
    show_default=True,
    help="Number of records to show.",
)
@click.option(
    "--clear", "-c",
    is_flag=True,
    default=False,
    help="Clear history.",
)
def history_cmd(limit: int, clear: bool) -> None:
    """
    Show request history.

    \b
    Examples:
      aero-openai history
      aero-openai history --limit 20
      aero-openai history --clear
    """
    if clear:
        deleted = history_clear()
        if deleted:
            print_success(f"History cleared. Removed {deleted} records.")
        else:
            print_info("History is already empty.")
        return

    records = history_get_all(limit=limit)
    print_history(records)


@click.command("stats")
def stats_cmd() -> None:
    """
    Show usage statistics.

    \b
    Example:
      aero-openai stats
    """
    stats = get_stats()

    if stats["total_requests"] == 0:
        print_info("No requests recorded yet.")
        return

    print_stats(stats)
