import os

import pytest

from openai_edition.api.aviationstack import AviationStackClient


pytestmark = pytest.mark.live_api


def _ensure_live_enabled():
    if os.getenv("RUN_LIVE_AVIATIONSTACK") != "1":
        pytest.skip("Set RUN_LIVE_AVIATIONSTACK=1 to run live AviationStack tests.")
    if not os.getenv("AVIATION_API_KEY"):
        pytest.skip("AVIATION_API_KEY is required for live AviationStack tests.")


def test_live_flights_endpoint_smoke():
    _ensure_live_enabled()

    client = AviationStackClient()
    payload = client._get("flights", {"limit": 1})

    assert isinstance(payload, dict)
    assert "data" in payload
    assert isinstance(payload["data"], list)

