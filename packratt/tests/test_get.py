from packratt.cache import Cache
from packratt.interface import get

from pathlib import Path
import pytest
import shutil

@pytest.mark.parametrize("google_key",
    ['/test/ms/2020-06-04/google/smallest_ms_truncated.tar.gz'])
@pytest.mark.parametrize("elwood_key",
    ['/test/ms/2020-06-04/elwood/smallest_ms_truncated.tar.gz'])
def test_get(google_key, elwood_key, test_cache, tmp_path_factory):
    google_dest = tmp_path_factory.mktemp("google")
    elwood_dest = tmp_path_factory.mktemp("elwood")

    google_md5 = get(google_key, google_dest)
    elwood_md5 = get(elwood_key, elwood_dest)

    assert google_md5 == elwood_md5


@pytest.mark.parametrize("partial_key",
    ['/test/ms/2020-06-04/elwood/smallest_ms_truncated.tar.gz'])
@pytest.mark.parametrize("elwood_key",
    ['/test/ms/2020-06-04/elwood/smallest_ms.tar.gz'])
def test_get_partial(elwood_key, partial_key, test_cache,
                     registry, tmp_path_factory):
    md5 = get(partial_key, tmp_path_factory.mktemp("ignore"))

    partial_file = Path(test_cache.cache_key_dir(partial_key),
                        Path(partial_key).name)

    elwood_dir = test_cache.cache_key_dir(elwood_key)
    elwood_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(partial_file, elwood_dir)

    dest = tmp_path_factory.mktemp("dest")

    assert get(elwood_key, dest) == registry[elwood_key]['hash']