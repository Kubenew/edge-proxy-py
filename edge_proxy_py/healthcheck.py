from __future__ import annotations

import asyncio
import logging

import httpx

from .router import Route
from .metrics import BACKEND_HEALTH

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient()
    return _client


async def close_healthcheck_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def _check(url: str, path: str, timeout_seconds: int, client: httpx.AsyncClient) -> bool:
    try:
        r = await client.get(url.rstrip("/") + path, timeout=timeout_seconds)
        return 200 <= r.status_code < 400
    except asyncio.CancelledError:
        raise
    except Exception:
        return False


async def loop(routes: list[Route], interval_seconds: int, timeout_seconds: int, path: str):
    client = _get_client()
    while True:
        try:
            backends = [b for r in routes for b in r.backends]
            checks = [_check(b.url, path, timeout_seconds, client) for b in backends]
            results = await asyncio.gather(*checks, return_exceptions=True)
            for backend, ok in zip(backends, results):
                backend.healthy = bool(ok)
                BACKEND_HEALTH.labels(backend=backend.url).set(1 if ok else 0)
            healthy_count = sum(1 for b in backends if b.healthy)
            if healthy_count != len(backends):
                logger.info("Healthcheck: %d/%d backends healthy", healthy_count, len(backends))
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Healthcheck loop error")

        await asyncio.sleep(interval_seconds)
