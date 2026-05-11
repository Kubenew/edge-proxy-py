from edge_proxy_py.router import Route
from edge_proxy_py.backends import Backend
from starlette.requests import Request


def _make_request(path: str, device_id: str | None = None) -> Request:
    headers = {}
    if device_id:
        headers["x-device-id"] = device_id
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "scheme": "http",
        "server": ("test", 80),
    }
    return Request(scope)


def test_match_path_prefix():
    r = Route(path_prefix="/api", device_id=None, backends=[Backend(url="http://localhost:8000")])
    assert r.matches(_make_request("/api/users"))
    assert r.matches(_make_request("/api"))
    assert not r.matches(_make_request("/other"))


def test_match_device_id():
    r = Route(path_prefix=None, device_id="sensor-1", backends=[Backend(url="http://localhost:8000")])
    assert r.matches(_make_request("/any", device_id="sensor-1"))
    assert not r.matches(_make_request("/any", device_id="sensor-2"))
    assert not r.matches(_make_request("/any"))


def test_match_both():
    r = Route(path_prefix="/api", device_id="sensor-1", backends=[Backend(url="http://localhost:8000")])
    assert r.matches(_make_request("/api/data", device_id="sensor-1"))
    assert not r.matches(_make_request("/other", device_id="sensor-1"))
    assert not r.matches(_make_request("/api/data", device_id="sensor-2"))


def test_match_no_constraints():
    r = Route(path_prefix=None, device_id=None, backends=[Backend(url="http://localhost:8000")])
    assert r.matches(_make_request("/anything"))


def test_choose_backend():
    r = Route(path_prefix=None, device_id=None, backends=[
        Backend(url="http://a", healthy=True, active_requests=5),
        Backend(url="http://b", healthy=True, active_requests=1),
    ])
    chosen = r.choose_backend()
    assert chosen is not None
    assert chosen.url == "http://b"


def test_choose_backend_all_unhealthy():
    r = Route(path_prefix=None, device_id=None, backends=[
        Backend(url="http://a", healthy=False),
    ])
    assert r.choose_backend() is None


def test_choose_backend_skips_unhealthy():
    r = Route(path_prefix=None, device_id=None, backends=[
        Backend(url="http://a", healthy=False),
        Backend(url="http://b", healthy=True),
    ])
    chosen = r.choose_backend()
    assert chosen.url == "http://b"
