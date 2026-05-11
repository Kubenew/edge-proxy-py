from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


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
        if time.time() - item.created > self.ttl_seconds:
            del self._data[key]
            return None
        return item

    def set(self, key: str, item: CacheItem):
        if len(self._data) >= self.max_items:
            oldest = min(self._data.items(), key=lambda kv: kv[1].created)[0]
            del self._data[oldest]
            logger.debug("Cache evicted oldest item %s", oldest)
        self._data[key] = item
        logger.debug("Cache set %s (%d items)", key, len(self._data))
