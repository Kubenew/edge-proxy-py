from __future__ import annotations

import asyncio
import typer
import uvicorn

from .config import load_config
from .router import Route
from .backends import Backend
from .cache import MemoryCache
from .healthcheck import loop as healthcheck_loop
from .app import create_app

app = typer.Typer(help="edge-proxy-py - edge/IoT adaptive reverse proxy")


@app.command()
def run(config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file")):
    cfg = load_config(config)

    routes = []
    for r in cfg.routes:
        routes.append(Route(
            path_prefix=r.match.path_prefix,
            device_id=r.match.device_id,
            backends=[Backend(url=b.url) for b in r.backends],
        ))

    cache = None
    if cfg.cache.enabled:
        cache = MemoryCache(ttl_seconds=cfg.cache.ttl_seconds, max_items=cfg.cache.max_items)

    host, port = "0.0.0.0", 9100
    if ":" in cfg.listen:
        host, port_str = cfg.listen.split(":", 1)
        port = int(port_str)

    app_instance = create_app(
        routes=routes,
        cache=cache,
        metrics_enabled=cfg.metrics.enabled,
        metrics_path=cfg.metrics.path,
    )

    loop = asyncio.get_event_loop()
    if cfg.healthcheck.enabled:
        loop.create_task(
            healthcheck_loop(
                routes=routes,
                interval_seconds=cfg.healthcheck.interval_seconds,
                timeout_seconds=cfg.healthcheck.timeout_seconds,
                path=cfg.healthcheck.path,
            )
        )

    uvicorn.run(app_instance, host=host, port=port)


if __name__ == "__main__":
    app()
