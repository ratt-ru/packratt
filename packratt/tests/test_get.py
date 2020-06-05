from packratt.interface import get


def test_get(test_cache, tmp_path_factory):
    google_dest = tmp_path_factory.mktemp("google")
    elwood_dest = tmp_path_factory.mktemp("elwood")

    google_md5 = get(
        '/test/ms/2020-06-04/google/smallest_ms.tar.gz', google_dest)
    elwood_md5 = get(
        '/test/ms/2020-06-04/elwood/smallest_ms.tar.gz', elwood_dest)

    assert google_md5 == elwood_md5
