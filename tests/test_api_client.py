"""Tests for examples/web-api/server.py — APIClient class."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def api_client(web_api_mod):
    """Fresh APIClient with high rate limit and single retry (no sleep on error)."""
    client = web_api_mod.APIClient(
        base_url="http://test.local",
        api_key="test-key-123",
        timeout=5,
        max_retries=1,  # 1 = fail immediately without sleeping on error
    )
    # Replace rate limiter with a permissive one so tests never block
    client.rate_limiter = web_api_mod.RateLimiter(max_calls=1000, period=60)
    return client


def mock_response(json_data: dict, status_code: int = 200):
    """Build a minimal mock httpx.Response."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()  # no-op for 2xx
    return resp


def mock_error_response(status_code: int):
    """Build a mock response whose raise_for_status raises HTTPStatusError."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.text = f"HTTP {status_code}"
    resp.raise_for_status.side_effect = httpx.HTTPStatusError(
        str(status_code), request=MagicMock(), response=resp
    )
    return resp


# ---------------------------------------------------------------------------
# _get_headers
# ---------------------------------------------------------------------------


def test_get_headers_returns_bearer_token(api_client):
    headers = api_client._get_headers()
    assert headers["Authorization"] == "Bearer test-key-123"
    assert headers["Content-Type"] == "application/json"


def test_get_headers_uses_configured_api_key(web_api_mod):
    client = web_api_mod.APIClient(base_url="http://x", api_key="my-secret-key")
    assert client._get_headers()["Authorization"] == "Bearer my-secret-key"


# ---------------------------------------------------------------------------
# get — happy path
# ---------------------------------------------------------------------------


async def test_get_uses_get_method(api_client):
    api_client.client.request = AsyncMock(return_value=mock_response({"data": []}))
    await api_client.get("/api/products")
    assert api_client.client.request.call_args.kwargs["method"] == "GET"


async def test_get_constructs_correct_url(api_client):
    api_client.client.request = AsyncMock(return_value=mock_response({}))
    await api_client.get("/api/orders")
    url = api_client.client.request.call_args.kwargs["url"]
    assert url == "http://test.local/api/orders"


async def test_get_passes_params(api_client):
    api_client.client.request = AsyncMock(return_value=mock_response({}))
    await api_client.get("/api/products", params={"category": "Electronics", "limit": 10})
    params = api_client.client.request.call_args.kwargs["params"]
    assert params == {"category": "Electronics", "limit": 10}


async def test_get_returns_parsed_json(api_client):
    expected = {"data": [{"id": "PROD001", "name": "Widget"}]}
    api_client.client.request = AsyncMock(return_value=mock_response(expected))
    result = await api_client.get("/api/products")
    assert result == expected


# ---------------------------------------------------------------------------
# post — happy path
# ---------------------------------------------------------------------------


async def test_post_uses_post_method(api_client):
    api_client.client.request = AsyncMock(return_value=mock_response({}))
    await api_client.post("/api/analytics/report", json_data={"metric": "page_views"})
    assert api_client.client.request.call_args.kwargs["method"] == "POST"


async def test_post_passes_json_body(api_client):
    api_client.client.request = AsyncMock(return_value=mock_response({}))
    payload = {"metric": "traffic_sources", "start_date": "2025-01-01"}
    await api_client.post("/api/analytics/report", json_data=payload)
    json_arg = api_client.client.request.call_args.kwargs["json"]
    assert json_arg == payload


async def test_post_returns_parsed_json(api_client):
    expected = {"data": [], "summary": {"total": 0}}
    api_client.client.request = AsyncMock(return_value=mock_response(expected))
    result = await api_client.post("/api/analytics/report")
    assert result == expected


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


async def test_request_raises_on_http_error(api_client):
    api_client.client.request = AsyncMock(return_value=mock_error_response(500))
    with pytest.raises(Exception, match="API error: 500"):
        await api_client.get("/api/broken")


async def test_request_raises_on_network_error(api_client):
    api_client.client.request = AsyncMock(
        side_effect=httpx.RequestError("connection refused", request=MagicMock())
    )
    with pytest.raises(Exception, match="Network error"):
        await api_client.get("/api/unreachable")


async def test_request_retries_correct_number_of_times(api_client, monkeypatch):
    """With max_retries=3, a persistent error triggers exactly 3 attempts."""
    api_client.max_retries = 3
    monkeypatch.setattr("asyncio.sleep", AsyncMock())  # skip backoff waits

    api_client.client.request = AsyncMock(return_value=mock_error_response(503))
    with pytest.raises(Exception):
        await api_client.get("/api/flaky")

    assert api_client.client.request.call_count == 3


async def test_request_succeeds_after_transient_error(api_client, monkeypatch):
    """Should return successfully if a later retry succeeds."""
    api_client.max_retries = 3
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    success_data = {"data": "ok"}
    api_client.client.request = AsyncMock(
        side_effect=[
            mock_error_response(503),
            mock_response(success_data),
        ]
    )
    result = await api_client.get("/api/eventually-ok")
    assert result == success_data
    assert api_client.client.request.call_count == 2
