from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class Backend:
    url: str
    healthy: bool = True
    active_requests: int = 0
    last_seen: float = field(default_factory=lambda: time.time())
