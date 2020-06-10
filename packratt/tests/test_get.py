from packratt.interface import get

from pathlib import Path
import pytest
import shutil


@pytest.mark.parametrize(
    "elwood_key", ['/test/ms/2020-06-04/elwood/smallest_ms.tar.gz'])
@pytest.mark.parametrize(
    "google_key", ['/test/ms/2020-06-04/google/smallest_ms.tar.gz'])
def test_get(google_key, elwood_key, test_cache, tmp_path_factory):
    google_dest = tmp_path_factory.mktemp("google")
    elwood_dest = tmp_path_factory.mktemp("elwood")

    google_md5 = get(google_key, google_dest)
    elwood_md5 = get(elwood_key, elwood_dest)

    assert google_md5 == elwood_md5


@pytest.mark.parametrize(
    "partial_key", ['/test/ms/2020-06-04/elwood/smallest_ms_truncated.tar.gz'])
@pytest.mark.parametrize(
    "elwood_key", ['/test/ms/2020-06-04/elwood/smallest_ms.tar.gz'])
@pytest.mark.parametrize(
    "google_key", ['/test/ms/2020-06-04/google/smallest_ms.tar.gz'])
def test_get_partial_ftp(partial_key, google_key, elwood_key,
                         test_cache, registry, tmp_path_factory):
    md5 = get(partial_key, tmp_path_factory.mktemp("ignore"))
    assert md5 == registry[partial_key]['hash']

    partial_file = Path(test_cache.cache_key_dir(partial_key),
                        Path(partial_key).name)

    # Create the cache directory for the full file
    elwood_dir = test_cache.cache_key_dir(elwood_key)
    elwood_dir.mkdir(parents=True, exist_ok=True)
    # Create the partial file
    partial_name = elwood_dir / '.'.join((Path(elwood_key).name, 'partial'))
    partial_path = Path(partial_name)
    full_path = Path(elwood_dir / Path(elwood_key).name)
    shutil.copyfile(partial_file, partial_path)

    dest = tmp_path_factory.mktemp("dest")

    assert not full_path.exists()
    assert partial_path.exists()
    assert get(elwood_key, dest) == registry[elwood_key]['hash']
    assert full_path.exists()
    assert not partial_path.exists()

    # Create the cache directory for the full file
    google_dir = test_cache.cache_key_dir(google_key)
    google_dir.mkdir(parents=True, exist_ok=True)
    # Create the partial file
    partial_name = google_dir / '.'.join((Path(google_key).name, 'partial'))
    partial_path = Path(partial_name)
    full_path = Path(google_dir / Path(google_key).name)
    shutil.copyfile(partial_file, partial_name)

    dest = tmp_path_factory.mktemp("dest")

    assert not full_path.exists()
    assert partial_path.exists()
    assert get(google_key, dest) == registry[google_key]['hash']
    assert full_path.exists()
    assert not partial_path.exists()
