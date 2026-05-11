from __future__ import annotations

import time
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response

from .router import Route
from .proxy import forward
from .cache import MemoryCache, CacheItem
from .metrics import (
    REQ_COUNT,
    CACHE_HITS,
    CACHE_MISSES,
    metrics_response,
)


def create_app(routes: list[Route], cache: MemoryCache | None, metrics_enabled: bool, metrics_path: str) -> FastAPI:
    app = FastAPI(title="edge-proxy-py")

    def match_route(request: Request) -> tuple[str, Route] | None:
        for idx, r in enumerate(routes):
            if r.matches(request):
                return f"route_{idx}", r
        return None

    @app.api_route("/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS","HEAD"])
    async def handler(request: Request):
        matched = match_route(request)
        if not matched:
            raise HTTPException(status_code=404, detail="No route matched")

        route_name, route = matched
        backend = route.choose_backend()

        cache_key = f"{request.method}:{request.url.path}?{request.url.query}:{request.headers.get('x-device-id','')}"

        # cache fallback only for GET
        if request.method == "GET" and cache:
            cached = cache.get(cache_key)
            if cached:
                CACHE_HITS.labels(route=route_name).inc()
                REQ_COUNT.labels(route=route_name, backend="cache", status=str(cached.status_code)).inc()
                return Response(
                    content=cached.value,
                    status_code=cached.status_code,
                    media_type=cached.content_type,
                )
            else:
                CACHE_MISSES.labels(route=route_name).inc()

        if not backend:
            # fallback to cache if available
            if request.method == "GET" and cache:
                cached = cache.get(cache_key)
                if cached:
                    return Response(
                        content=cached.value,
                        status_code=cached.status_code,
                        media_type=cached.content_type,
                    )
            raise HTTPException(status_code=503, detail="No healthy backend available")

        backend.active_requests += 1
        try:
            resp = await forward(request, backend.url)
        finally:
            backend.active_requests -= 1

        REQ_COUNT.labels(route=route_name, backend=backend.url, status=str(resp.status_code)).inc()

        if request.method == "GET" and cache and resp.status_code == 200:
            cache.set(cache_key, CacheItem(
                value=resp.body,
                content_type=resp.media_type or "application/octet-stream",
                status_code=resp.status_code,
                created=time.time(),
            ))

        return resp

    if metrics_enabled:
        @app.get(metrics_path)
        async def metrics():
            return metrics_response()

    return app
