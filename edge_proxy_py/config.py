from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional
import yaml


class BackendConfig(BaseModel):
    url: str


class MatchConfig(BaseModel):
    path_prefix: Optional[str] = None
    device_id: Optional[str] = None


class RouteConfig(BaseModel):
    match: MatchConfig
    backends: List[BackendConfig] = Field(default_factory=list)


class CacheConfig(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 30
    max_items: int = 200


class HealthcheckConfig(BaseModel):
    enabled: bool = True
    interval_seconds: int = 5
    timeout_seconds: int = 2
    path: str = "/health"


class MetricsConfig(BaseModel):
    enabled: bool = True
    path: str = "/metrics"


class AppConfig(BaseModel):
    listen: str = "0.0.0.0:9100"
    routes: List[RouteConfig] = Field(default_factory=list)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    healthcheck: HealthcheckConfig = Field(default_factory=HealthcheckConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AppConfig.model_validate(raw)
