from edge_proxy_py.cache import MemoryCache, CacheItem
import time


def test_cache_set_get():
    c = MemoryCache(ttl_seconds=2, max_items=10)
    c.set("k", CacheItem(value=b"abc", content_type="text/plain", status_code=200, created=time.time()))
    assert c.get("k") is not None
