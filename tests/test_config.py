from edge_proxy_py.config import load_config, CacheConfig


def test_load_config(tmp_path):
    cfg_file = tmp_path / "config.yml"
    cfg_file.write_text("""
listen: "0.0.0.0:9200"
routes:
  - match:
      path_prefix: "/api"
    backends:
      - url: "http://localhost:8000"
cache:
  enabled: true
  ttl_seconds: 60
  max_items: 500
""")
    cfg = load_config(str(cfg_file))
    assert cfg.listen == "0.0.0.0:9200"
    assert len(cfg.routes) == 1
    assert cfg.routes[0].match.path_prefix == "/api"
    assert cfg.routes[0].backends[0].url == "http://localhost:8000"
    assert cfg.cache.ttl_seconds == 60


def test_load_config_defaults(tmp_path):
    cfg_file = tmp_path / "config.yml"
    cfg_file.write_text("routes:\n  - match:\n      path_prefix: /\n    backends:\n      - url: http://localhost:8000\n")
    cfg = load_config(str(cfg_file))
    assert cfg.listen == "0.0.0.0:9100"
    assert cfg.healthcheck.interval_seconds == 5
    assert cfg.cache.max_items == 200


def test_load_config_empty(tmp_path):
    cfg_file = tmp_path / "config.yml"
    cfg_file.write_text("")
    cfg = load_config(str(cfg_file))
    assert len(cfg.routes) == 0
    assert cfg.listen == "0.0.0.0:9100"


def test_load_config_missing_file():
    import pytest
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/config.yml")


def test_cache_config_defaults():
    c = CacheConfig()
    assert c.enabled is True
    assert c.ttl_seconds == 30
    assert c.max_items == 200
