"""
Redis cache abstraction layer.

Provides a CacheBackend protocol and a NullCache implementation for MVP.
Swap NullCache for RedisCache when Redis infrastructure is available.
"""

from typing import Any, Protocol


class CacheBackend(Protocol):
    """Abstract cache interface — any backend must implement these methods."""

    async def get(self, key: str) -> Any | None: ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def exists(self, key: str) -> bool: ...

    async def flush(self) -> None: ...


class NullCache:
    """No-op cache for local development without Redis."""

    async def get(self, key: str) -> Any | None:
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def exists(self, key: str) -> bool:
        return False

    async def flush(self) -> None:
        pass


# Singleton — swap this with RedisCache in production
_cache: CacheBackend = NullCache()


def get_cache() -> CacheBackend:
    return _cache


def set_cache_backend(backend: CacheBackend) -> None:
    global _cache
    _cache = backend
