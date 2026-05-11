import pytest

from edge_proxy_py.healthcheck import _check, close_healthcheck_client


@pytest.mark.asyncio
async def test_check_healthy(httpserver):
    httpserver.serve_content(content="ok", code=200)
    client = __import__("edge_proxy_py.healthcheck", fromlist=["_get_client"])._get_client()
    result = await _check(httpserver.url, "/health", 2, client)
    assert result is True
    await close_healthcheck_client()


@pytest.mark.asyncio
async def test_check_unhealthy(httpserver):
    httpserver.serve_content(content="error", code=500)
    client = __import__("edge_proxy_py.healthcheck", fromlist=["_get_client"])._get_client()
    result = await _check(httpserver.url, "/health", 2, client)
    assert result is False
    await close_healthcheck_client()


@pytest.mark.asyncio
async def test_check_connection_refused():
    client = __import__("edge_proxy_py.healthcheck", fromlist=["_get_client"])._get_client()
    result = await _check("http://localhost:1", "/health", 1, client)
    assert result is False
    await close_healthcheck_client()
