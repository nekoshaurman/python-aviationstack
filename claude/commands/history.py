import click

from claude.db.database import history_get_all, history_clear, get_stats
from claude.utils.display import (
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
    help="Количество записей.",
)
@click.option(
    "--clear", "-c",
    is_flag=True,
    default=False,
    help="Очистить историю.",
)
def history_cmd(limit: int, clear: bool) -> None:
    """
    История всех запросов.

    \b
    Примеры:
      aero history
      aero history --limit 20
      aero history --clear
    """
    if clear:
        deleted = history_clear()
        if deleted:
            print_success(f"История очищена. Удалено записей: {deleted}.")
        else:
            print_info("История уже пуста.")
        return

    records = history_get_all(limit=limit)
    print_history(records)


@click.command("stats")
def stats_cmd() -> None:
    """
    Статистика использования приложения.

    \b
    Пример:
      aero stats
    """
    stats = get_stats()

    if stats["total_requests"] == 0:
        print_info("Статистика пуста — ещё не было ни одного запроса.")
        return

    print_stats(stats)