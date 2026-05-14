from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from starlette.requests import Request

from .backends import Backend


@dataclass
class Route:
    path_prefix: Optional[str]
    device_id: Optional[str]
    backends: List[Backend]

    def matches(self, request: Request) -> bool:
        if self.path_prefix:
            path = request.url.path
            prefix = self.path_prefix
            if not path.startswith(prefix):
                return False
            if prefix != "/" and len(path) > len(prefix) and path[len(prefix)] != "/":
                return False

        if self.device_id:
            if request.headers.get("x-device-id") != self.device_id:
                return False

        return True

    def choose_backend(self) -> Optional[Backend]:
        healthy = [b for b in self.backends if b.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda b: b.active_requests)
