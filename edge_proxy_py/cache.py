from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class CacheItem:
    value: bytes
    content_type: str
    status_code: int
    created: float


class MemoryCache:
    def __init__(self, ttl_seconds: int, max_items: int):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._data: Dict[str, CacheItem] = {}

    def get(self, key: str) -> Optional[CacheItem]:
        item = self._data.get(key)
        if not item:
            return None

        if (time.time() - item.created) > self.ttl_seconds:
            self._data.pop(key, None)
            return None

        return item

    def set(self, key: str, item: CacheItem):
        if len(self._data) >= self.max_items:
            # naive eviction: remove oldest
            oldest = min(self._data.items(), key=lambda kv: kv[1].created)[0]
            self._data.pop(oldest, None)

        self._data[key] = item
