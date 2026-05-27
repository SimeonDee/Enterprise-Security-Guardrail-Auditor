import pytest

from app.core.cache import NullCache, get_cache, set_cache_backend


@pytest.mark.asyncio
async def test_null_cache_get_returns_none():
    cache = NullCache()
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_null_cache_set_does_nothing():
    cache = NullCache()
    await cache.set("key", "value", ttl=60)
    assert await cache.get("key") is None


@pytest.mark.asyncio
async def test_null_cache_exists_returns_false():
    cache = NullCache()
    assert await cache.exists("key") is False


@pytest.mark.asyncio
async def test_null_cache_delete():
    cache = NullCache()
    await cache.delete("key")  # should not raise


@pytest.mark.asyncio
async def test_null_cache_flush():
    cache = NullCache()
    await cache.flush()  # should not raise


def test_get_cache_returns_null_cache():
    cache = get_cache()
    assert isinstance(cache, NullCache)


def test_set_cache_backend():
    original = get_cache()
    new_cache = NullCache()
    set_cache_backend(new_cache)
    assert get_cache() is new_cache
    set_cache_backend(original)
