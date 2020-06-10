from contextlib import contextmanager
from ftplib import FTP
import hashlib
import logging
import shutil
from urllib.parse import urlparse

import requests

from packratt.dispatch import Dispatch

log = logging.getLogger(__name__)

downloaders = Dispatch()

# 32k chunks
CHUNK_SIZE = 2**15


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


def requests_partial_download(entry, url, session,
                              response, params=None):
    part_filename = entry['dir'] / '.'.join((entry['filename'], 'partial'))
    filename = entry['dir'] / entry['filename']

    if params is None:
        params = {}

    with open_and_hash_file(part_filename) as (size, md5hash, f):
        if size > 0:
            log.info("Resuming download of %s at %d", filename, size)
            # Some of this file has already been downloaded
            # Request the rest of it
            total_size = int(response.headers['Content-Length'])
            response.close()
            headers = {'Range': 'bytes=%d-%d' % (size, total_size)}
            response = session.get(url, params=params,
                                   headers=headers, stream=True)

        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                md5hash.update(chunk)
                f.write(chunk)

    shutil.move(part_filename, filename)
    return md5hash.hexdigest()


@downloaders.register("google")
def download_google_drive(entry):
    url = "https://drive.google.com/uc?export=download"
    params = {'id': entry['file_id']}

    with requests.Session() as session:
        response = session.get(url, params=params, stream=True)

        try:
            # Look for a token indicating a large file
            # Re-request with confirmation token
            for key, value in response.cookies.items():
                if key.startswith('download_warning'):
                    params['confim'] = value
                    response.close()
                    response = session.get(url, params=params, stream=True)
                    break

            return requests_partial_download(entry, url,
                                             session, response,
                                             params=params)
        finally:
            response.close()


def download_ftp(entry, url):
    part_filename = entry['dir'] / '.'.join((entry['filename'], 'partial'))
    filename = entry['dir'] / entry['filename']

    with open_and_hash_file(part_filename) as (size, md5hash, f):
        if size > 0:
            log.info("Resuming download of %s at %d", part_filename, size)

        ftp = FTP(url.hostname)

        def callback(data):
            f.write(data)
            md5hash.update(data)

        try:
            ftp.login(url.username, url.password)
            ftp.retrbinary("RETR %s" % url.path, callback,
                           blocksize=CHUNK_SIZE, rest=size)

            shutil.move(part_filename, filename)
        finally:
            ftp.quit()

        return md5hash.hexdigest()


@downloaders.register("url")
def download_url(entry):
    # requests doesn't handle ftp
    parsed_url = urlparse(entry['url'])

    if parsed_url.scheme == "ftp":
        return download_ftp(entry, parsed_url)

    # Use requests for (presumably) http cases
    with requests.Session() as session:
        response = session.get(entry['url'], stream=True)

        try:
            return requests_partial_download(entry, entry['url'],
                                             session, response)
        finally:
            response.close()
