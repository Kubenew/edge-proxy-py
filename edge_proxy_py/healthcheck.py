from __future__ import annotations

import asyncio
import httpx

from .router import Route
from .metrics import BACKEND_HEALTH


async def _check(url: str, path: str, timeout_seconds: int) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            r = await client.get(url.rstrip("/") + path)
            return 200 <= r.status_code < 400
    except Exception:
        return False


async def loop(routes: list[Route], interval_seconds: int, timeout_seconds: int, path: str):
    while True:
        for route in routes:
            for backend in route.backends:
                backend.healthy = await _check(backend.url, path, timeout_seconds)
                BACKEND_HEALTH.labels(backend=backend.url).set(1 if backend.healthy else 0)
        await asyncio.sleep(interval_seconds)
