import json
from typing import Optional, Any
import redis
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()

try:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


class Cache:
    def __init__(self, prefix: str = "wineapi:", ttl: int = 300):
        self.prefix = prefix
        self.ttl = ttl
        self.client = redis_client

    def get(self, key: str) -> Optional[Any]:
        if not REDIS_AVAILABLE:
            return None
        try:
            value = self.client.get(f"{self.prefix}{key}")
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if not REDIS_AVAILABLE:
            return False
        try:
            self.client.setex(
                f"{self.prefix}{key}",
                ttl or self.ttl,
                json.dumps(value),
            )
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        if not REDIS_AVAILABLE:
            return False
        try:
            self.client.delete(f"{self.prefix}{key}")
            return True
        except Exception:
            return False

    def invalidate_prefix(self, prefix: str) -> bool:
        if not REDIS_AVAILABLE:
            return False
        try:
            keys = self.client.keys(f"{self.prefix}{prefix}*")
            if keys:
                self.client.delete(*keys)
            return True
        except Exception:
            return False


stats_cache = Cache(prefix="stats:", ttl=600)
regions_cache = Cache(prefix="regions:", ttl=3600)
varieties_cache = Cache(prefix="varieties:", ttl=3600)
