from __future__ import annotations

import asyncio
import logging
import signal

import typer
import uvicorn

from .app import create_app
from .backends import Backend
from .cache import MemoryCache
from .config import load_config
from .healthcheck import close_healthcheck_client, loop as healthcheck_loop
from .router import Route

logger = logging.getLogger("edge_proxy_py")

app = typer.Typer(help="edge-proxy-py - edge/IoT adaptive reverse proxy")

_log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@app.command()
def run(
    config: str = typer.Option(..., "--config", "-c", help="Path to YAML config file"),
    log_level: str = typer.Option("INFO", "--log-level", help="Log level: DEBUG, INFO, WARNING, ERROR"),
):
    logging.basicConfig(level=_log_levels.get(log_level.upper(), logging.INFO), format="%(levelname)s %(name)s: %(message)s")

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
    hc_task: asyncio.Task | None = None
    if cfg.healthcheck.enabled:
        hc_task = loop.create_task(
            healthcheck_loop(
                routes=routes,
                interval_seconds=cfg.healthcheck.interval_seconds,
                timeout_seconds=cfg.healthcheck.timeout_seconds,
                path=cfg.healthcheck.path,
            )
        )

    stop_event = asyncio.Event()

    def _signal_handler():
        logger.info("Shutdown signal received...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass

    config = uvicorn.Config(app_instance, host=host, port=port)
    server = uvicorn.Server(config)

    async def wait_for_shutdown():
        await stop_event.wait()
        if hc_task:
            hc_task.cancel()
            try:
                await hc_task
            except asyncio.CancelledError:
                pass
        await close_healthcheck_client()
        server.should_exit = True

    loop.create_task(wait_for_shutdown())

    server.run()


if __name__ == "__main__":
    app()
