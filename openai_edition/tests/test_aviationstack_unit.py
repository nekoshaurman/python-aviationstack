import pytest
import requests

from openai_edition.api.aviationstack import AviationStackClient, AviationStackError
from openai_edition.db import database


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, url="http://example.test", text="{}"):
        self.status_code = status_code
        self._json_data = {} if json_data is None else json_data
        self.url = url
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(response=self)

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data


def test_get_raises_on_timeout(monkeypatch):
    client = AviationStackClient()

    def _timeout(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "get", _timeout)

    with pytest.raises(AviationStackError, match="did not respond"):
        client._get("flights", {})


def test_get_raises_on_connection_error(monkeypatch):
    client = AviationStackClient()

    def _connection_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(requests, "get", _connection_error)

    with pytest.raises(AviationStackError, match="No internet connection"):
        client._get("flights", {})


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (429, "Rate limit exceeded"),
        (403, "not available on the free plan"),
        (500, "HTTP error: 500"),
    ],
)
def test_get_raises_on_http_errors(monkeypatch, status_code, message):
    client = AviationStackClient()

    def _fake_get(*args, **kwargs):
        return DummyResponse(status_code=status_code)

    monkeypatch.setattr(requests, "get", _fake_get)

    with pytest.raises(AviationStackError, match=message):
        client._get("flights", {})


def test_get_handles_json_error_payload_rate_limit(monkeypatch):
    client = AviationStackClient()

    payload = {
        "error": {
            "code": "usage_limit_reached",
            "info": "Monthly quota reached.",
        }
    }

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: DummyResponse(json_data=payload))

    with pytest.raises(AviationStackError, match="Rate limit exceeded"):
        client._get("flights", {})


def test_get_handles_json_error_payload_generic(monkeypatch):
    client = AviationStackClient()

    payload = {
        "error": {
            "code": "invalid_access_key",
            "info": "Access key is invalid.",
        }
    }

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: DummyResponse(json_data=payload))

    with pytest.raises(AviationStackError, match=r"\[invalid_access_key\] Access key is invalid\."):
        client._get("flights", {})


def test_get_airport_prefers_exact_iata_match(monkeypatch):
    client = AviationStackClient()

    airports_payload = {
        "data": [
            {"iata_code": "SVQ", "airport_name": "Seville"},
            {"iata_code": "SVO", "airport_name": "Sheremetyevo"},
        ]
    }

    monkeypatch.setattr(client, "_get", lambda endpoint, params: airports_payload)

    result = client.get_airport("svo")
    assert result["iata_code"] == "SVO"
    assert result["airport_name"] == "Sheremetyevo"


def test_get_airline_uses_cache_without_extra_api_calls(monkeypatch):
    cached = {"iata_code": "LH", "airline_name": "Lufthansa"}
    database.airline_cache_set("LH", cached)

    client = AviationStackClient()

    def _should_not_call_api(*args, **kwargs):
        raise AssertionError("API call should not happen when airline is already cached.")

    monkeypatch.setattr(client, "_get", _should_not_call_api)

    result = client.get_airline("lh")
    assert result == cached

