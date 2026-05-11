import time

from edge_proxy_py.cache import MemoryCache, CacheItem


def test_cache_set_get():
    c = MemoryCache(ttl_seconds=2, max_items=10)
    c.set("k", CacheItem(value=b"abc", content_type="text/plain", status_code=200, created=time.time()))
    assert c.get("k") is not None
    assert c.get("k").value == b"abc"


def test_cache_expiry():
    c = MemoryCache(ttl_seconds=0, max_items=10)
    c.set("k", CacheItem(value=b"abc", content_type="text/plain", status_code=200, created=time.time() - 10))
    assert c.get("k") is None


def test_cache_miss():
    c = MemoryCache(ttl_seconds=10, max_items=10)
    assert c.get("nonexistent") is None


def test_cache_eviction():
    c = MemoryCache(ttl_seconds=10, max_items=2)
    c.set("a", CacheItem(value=b"1", content_type="text/plain", status_code=200, created=time.time()))
    c.set("b", CacheItem(value=b"2", content_type="text/plain", status_code=200, created=time.time()))
    c.set("c", CacheItem(value=b"3", content_type="text/plain", status_code=200, created=time.time()))
    assert c.get("a") is None
    assert c.get("b") is not None
    assert c.get("c") is not None


def test_cache_overwrite():
    c = MemoryCache(ttl_seconds=10, max_items=10)
    c.set("k", CacheItem(value=b"old", content_type="text/plain", status_code=200, created=time.time()))
    c.set("k", CacheItem(value=b"new", content_type="text/plain", status_code=200, created=time.time()))
    assert c.get("k").value == b"new"
