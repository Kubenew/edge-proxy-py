# edge-proxy-py

**edge-proxy-py** is a lightweight reverse proxy designed for **edge / IoT deployments**.

Focus:
- offline/unstable network conditions
- routing policies (geo/device/priority)
- local cache fallback
- health checks and telemetry

## MVP Features
- Reverse proxy gateway for edge services
- Policy-based routing (device-id header / path rules)
- Backend health checking
- Simple in-memory cache fallback for GET requests
- Prometheus metrics
- YAML config

## Quickstart

```bash
pip install -e .
edge-proxy run -c examples/config.yml
```

Test:
```bash
curl -H "X-Device-ID: sensor-1" http://localhost:9100/api/data
```

## Roadmap
- persistent cache (sqlite/rocksdb)
- mqtt proxy mode
- grpc support
- edge federation (multi-node routing)
- bandwidth shaping + compression
