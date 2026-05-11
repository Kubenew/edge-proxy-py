from __future__ import annotations

import asyncio
import logging

import httpx
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

HOP_BY_HOP_HEADERS = frozenset({
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
})

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(follow_redirects=False, timeout=30)
    return _client


async def close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _filter_headers(headers: dict) -> dict:
    return {k: v for k, v in headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}


async def forward(request: Request, backend_url: str) -> Response:
    target = backend_url.rstrip("/") + request.url.path
    if request.url.query:
        target += "?" + request.url.query

    body = await request.body()
    client = _get_client()

    try:
        resp = await client.request(
            method=request.method,
            url=target,
            headers=_filter_headers(dict(request.headers)),
            content=body,
        )
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Failed to forward request to %s", backend_url)
        raise

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=_filter_headers(dict(resp.headers)),
        media_type=resp.headers.get("content-type"),
    )
