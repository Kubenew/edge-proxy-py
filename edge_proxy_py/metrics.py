from __future__ import annotations

from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


REQ_COUNT = Counter(
    "edge_proxy_requests_total",
    "Total requests processed",
    ["route", "backend", "status"],
)

CACHE_HITS = Counter(
    "edge_proxy_cache_hits_total",
    "Cache hits",
    ["route"],
)

CACHE_MISSES = Counter(
    "edge_proxy_cache_misses_total",
    "Cache misses",
    ["route"],
)

BACKEND_HEALTH = Gauge(
    "edge_proxy_backend_health",
    "Backend health status (1=healthy,0=down)",
    ["backend"],
)


def metrics_response() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
