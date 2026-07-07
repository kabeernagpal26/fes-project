import time
from typing import Any, Dict, Optional, Tuple
from app.config import settings

class InMemoryCache:
    """Thread-safe-like in-memory key-value cache with expirations."""
    def __init__(self):
        self._data: Dict[str, Tuple[str, Optional[float]]] = {}

    def get(self, key: str) -> Optional[str]:
        if key not in self._data:
            return None
        val, expiry = self._data[key]
        if expiry is not None and time.time() > expiry:
            del self._data[key]
            return None
        return val

    def set(self, key: str, value: str, expire: int = 3600):
        expiry = time.time() + expire if expire else None
        self._data[key] = (value, expiry)

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]

    def delete_pattern(self, pattern: str):
        # We handle wildcards at the end e.g. "portfolio:1:*" -> starts with "portfolio:1:"
        prefix = pattern.replace("*", "")
        keys_to_del = [k for k in self._data.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            del self._data[k]

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.in_memory = InMemoryCache()
        
        if settings.REDIS_URL:
            try:
                import redis
                # Decode responses automatically to return str instead of bytes
                self.redis_client = redis.Redis.from_url(
                    settings.REDIS_URL, 
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                # Test connection
                self.redis_client.ping()
            except Exception:
                # Gracefully disable Redis on connection failure
                self.redis_client = None

    def get(self, key: str) -> Optional[str]:
        if self.redis_client is not None:
            try:
                return self.redis_client.get(key)
            except Exception:
                pass
        return self.in_memory.get(key)

    def set(self, key: str, value: str, expire: int = 3600):
        if self.redis_client is not None:
            try:
                self.redis_client.setex(key, expire, value)
                return
            except Exception:
                pass
        self.in_memory.set(key, value, expire)

    def delete(self, key: str):
        if self.redis_client is not None:
            try:
                self.redis_client.delete(key)
                return
            except Exception:
                pass
        self.in_memory.delete(key)

    def delete_pattern(self, pattern: str):
        if self.redis_client is not None:
            try:
                cursor = 0
                while True:
                    cursor, keys = self.redis_client.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
                return
            except Exception:
                pass
        self.in_memory.delete_pattern(pattern)

cache_service = CacheService()
