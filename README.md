# edge-proxy-py

[![PyPI](https://img.shields.io/pypi/v/edge-proxy-py)](https://pypi.org/project/edge-proxy-py/)
[![Python Versions](https://img.shields.io/pypi/pyversions/edge-proxy-py)](https://pypi.org/project/edge-proxy-py/)
[![License](https://img.shields.io/pypi/l/edge-proxy-py)](https://github.com/Kubenew/edge-proxy-py/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Kubenew/edge-proxy-py?style=flat&logo=github)](https://github.com/Kubenew/edge-proxy-py)
[![Downloads](https://img.shields.io/pepy.tech/dt/edge-proxy-py)](https://pepy.tech/project/edge-proxy-py)

**edge-proxy-py** is a lightweight reverse proxy designed for **edge / IoT deployments**.

Focus:
- offline/unstable network conditions
- routing policies (geo/device/priority)
- local cache fallback
- health checks and telemetry

## Features

- Reverse proxy gateway for edge services
- Policy-based routing (device-id header / path rules)
- Concurrent backend health checking with connection pooling
- In-memory cache fallback for GET requests (TTL-based with LRU-like eviction)
- Prometheus metrics (request count, cache hits/misses, backend health)
- Graceful shutdown (SIGINT/SIGTERM)

## Quickstart

### Install

```bash
pip install edge-proxy-py
```

### Run

```bash
edge-proxy run -c examples/config.yml
```

### Test

```bash
curl -H "X-Device-ID: sensor-1" http://localhost:9100/api/data
```

## Architecture

```
Client ──► edge-proxy ──► Route matching (path_prefix / device_id)
                              │
                         ┌────▼────┐
                         │  Cache  │──► Return cached response (GET only)
                         └────┬────┘
                              │ miss
                         ┌────▼────┐
                         │ Backend │──► forward() via httpx connection pool
                         └────┬────┘
                              ▼
                       Upstream server
```

## Changelog

### 0.1.1

- **Connection pooling**: Shared `httpx.AsyncClient` singleton for proxy and healthcheck (was creating a client per request/check).
- **Concurrent health checks**: Backends checked in parallel via `asyncio.gather` (was sequential).
- **Graceful shutdown**: Signal handlers (SIGINT/SIGTERM) cancel healthcheck loop and close clients cleanly.
- **Logging**: Added structured `logging` throughout; `--log-level` CLI option.
- **Bare except fixes**: All `except Exception` blocks re-raise `asyncio.CancelledError`.
- **Build system**: Migrated from `setuptools` to `hatchling`. Added classifiers, keywords, optional dev/test deps, ruff/pytest config.
- **Tests**: Expanded from 1 test to 15+ tests covering config, router, cache, proxy, healthcheck, and backends.
- **CI**: Added GitHub Actions workflow (ruff + pytest on 3.10–3.12).

### 0.1.0

- Initial release: Reverse proxy, policy-based routing, cache fallback, health checks, Prometheus metrics.

## License

MIT
