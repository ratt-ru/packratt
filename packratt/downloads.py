from contextlib import closing, contextmanager
from ftplib import FTP
import hashlib
from urllib.parse import urlparse
import urllib.request as request

import requests

from packratt.dispatch import Dispatch

downloaders = Dispatch()

CHUNK_SIZE = 2**20


@contextmanager
def open_and_hash_file(filename):
    md5hash = hashlib.md5()
    size = 0

    if filename.is_file():
        # File exists, hash contents and determine existing size
        # This also moves the file pointer to the end of the file
        f = open(filename, "rb+")

        while True:
            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            md5hash.update(chunk)
            size += len(chunk)
    else:
        # Open a new file for writing
        f = open(filename, "wb")

    try:
        yield size, md5hash, f
    finally:
        f.close()


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
                    params['confim'] = value
                    response.close()
                    response = session.get(URL, params=params, stream=True)
                    break


            with open_and_hash_file(filename) as (size, md5hash, f):
                if size > 0:
                    # Some of this file has already been downloaded
                    # Request the rest of it
                    total_size = response.headers['Content-Length']
                    response.close()
                    headers = {'Range': 'bytes=%d-%d' % (size, total_size)}
                    response = session.get(URL, params=params,
                                           headers=headers,
                                           stream=True)

                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        md5hash.update(chunk)
                        f.write(chunk)

                return md5hash.hexdigest()
        finally:
            response.close()


def download_ftp(entry, url, filename):
    with open_and_hash_file(filename) as (size, md5hash, f):
        ftp = FTP(url.hostname)

        def callback(data):
            f.write(data)
            md5hash.update(data)

        try:
            ftp.login(url.username, url.password)
            ftp.retrbinary("RETR %s" % url.path, callback,
                            blocksize=CHUNK_SIZE, rest=size)
        finally:
            ftp.quit()

        return md5hash.hexdigest()


@downloaders.register("url")
def download_url(entry):
    filename = entry['dir'] / entry['filename']

    # requests doesn't handle ftp
    url = urlparse(entry['url'])

    if url.scheme == "ftp":
        return download_ftp(entry, url, filename)

    # Use requests
    with requests.Session() as session:
        with session.get(entry['url'], stream=True) as response:
            with open_and_hash_file(filename) as (size, md5hash, f):
                for chunk in response.iter_content(CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        md5hash.update(chunk)
                        f.write(chunk)

                return md5hash.hexdigest()
