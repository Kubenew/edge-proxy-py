from edge_proxy_py.backends import Backend
import time


def test_backend_defaults():
    b = Backend(url="http://localhost:8000")
    assert b.healthy is True
    assert b.active_requests == 0
    assert abs(b.last_seen - time.time()) < 1


def test_backend_url():
    b = Backend(url="http://localhost:8000")
    assert b.url == "http://localhost:8000"


def test_backend_healthy_flag():
    b = Backend(url="http://localhost:8000")
    assert b.healthy is True
    b.healthy = False
    assert b.healthy is False
