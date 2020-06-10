from packratt.cache import get_cache, set_cache, Cache
from packratt.registry import load_registry

import pytest


@pytest.fixture(scope="session", autouse=True)
def global_test_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp('cache')
    set_cache(Cache(cache_dir))


@pytest.fixture
def test_cache(tmp_path_factory):
    cache_dir = tmp_path_factory.mktemp('cache')

    old_cache = get_cache()

    try:
        new_cache = Cache(cache_dir)
        set_cache(new_cache)
        yield new_cache
    finally:
        set_cache(old_cache)


@pytest.fixture(scope="session")
def registry():
    return load_registry()
