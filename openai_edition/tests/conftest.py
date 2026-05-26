import pytest
import requests

from openai_edition.db import database


@pytest.fixture(autouse=True)
def temp_db_path(tmp_path, monkeypatch):
    db_file = tmp_path / "openai_aerotrack_test.db"
    monkeypatch.setattr(database, "DB_PATH", str(db_file))
    database.init_db()
    return db_file


@pytest.fixture(autouse=True)
def test_api_key(request, monkeypatch):
    if request.node.get_closest_marker("live_api"):
        return
    monkeypatch.setenv("AVIATION_API_KEY", "test-api-key")


@pytest.fixture(autouse=True)
def block_network_by_default(request, monkeypatch):
    if request.node.get_closest_marker("live_api"):
        return

    def _blocked_get(*args, **kwargs):
        raise AssertionError(
            "Network access is blocked in tests. "
            "Use @pytest.mark.live_api to allow real API calls."
        )

    monkeypatch.setattr(requests, "get", _blocked_get)
