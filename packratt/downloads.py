from contextlib import closing
import hashlib
from urllib.parse import urlparse
import urllib.request as request

import requests

from packratt.dispatch import Dispatch

downloaders = Dispatch()

CHUNK_SIZE = 2**20


@downloaders.register("google")
def download_google_drive(entry):
    filename = entry['dir'] / entry['filename']

    URL = URL = "https://drive.google.com/uc?export=download"
    params = {'id': entry['file_id']}

    with requests.Session() as session:
        response = session.get(URL, params=params, stream=True)

        try:
            # Look for a token indicating a large file
            # Re-request with confirmation token
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    response.close()
                    params = {'id': entry['file_id'], 'confirm': value}
                    response = session.get(URL, params=params, stream=True)
                    break

            with open(filename, "wb") as f:
                hash_md5 = hashlib.md5()

                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        hash_md5.update(chunk)
                        f.write(chunk)

                return hash_md5.hexdigest()
        finally:
            response.close()


def download_ftp(entry, filename):
    with closing(request.urlopen(entry['url'])) as response:
        hash_md5 = hashlib.md5()

        with open(filename, 'wb') as f:
            while True:
                chunk = response.read(CHUNK_SIZE)

                if not chunk:
                    break

                hash_md5.update(chunk)
                f.write(chunk)

        return hash_md5.hexdigest()


@downloaders.register("url")
def download_url(entry):
    filename = entry['dir'] / entry['filename']

    # requests doesn't handle ftp
    if urlparse(entry['url']).scheme == "ftp":
        return download_ftp(entry, filename)

    # Use requests
    with requests.Session() as session:
        with session.get(entry['url'], stream=True) as response:
            with open(filename, "wb") as f:
                hash_md5 = hashlib.md5()

                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        hash_md5.update(chunk)
                        f.write(chunk)

                return hash_md5.hexdigest()
