packratt
========

``packratt`` is an application and a python package for downloading and
caching Radio Astronomy products, primarily to facilitate testing Radio
Astronomy software.

Installing
----------

For the lastest stable release

.. code:: bash

   $ pip install packratt

Usage
-----

Use an an linux application

.. code:: bash

   packratt get /ms/<telescope>/<observation_data>/<filename> <target_dir>
   packratt get /uvfits/<telescope>/<observation_date>/<filename> <target_dir>
   packratt get /beams/<telescope>/<filename> <target_dir>
   packratt get /gains/<telescope>/<observation_date>/<filename> <target_dir>

Use within a Python software package

.. code:: python

   import packratt

   packratt.get("/ms/<telescope>/<observation_data>/<filename>", target_dir)
   packratt.get("/uvfits/<telescope>/<observation_date>/<filename>", target_dir)
   packratt.get("/beams/<telescope>/<filename", target_dir)
   packratt.get("/gains/<telescope>/<observation_date>/<filename>", target_dir)

Registry schemas
~~~~~~~~~~~~~~~~

Schemas are defined by a yaml registry file and specify the type, location
and hash of the file to download. Currently, Standard url's and
Google Drive links are supported.

A standard URL entry might look like this:

.. code:: yaml

   '/test/ms/2020-06-04/elwood/smallest_ms.tar.gz':
     type: url
     url: ftp://elwood.ru.ac.za/pub/sjperkins/data/test/smallest_ms.tar.gz
     hash: 9d6379b5ad01a1fe6ec218d4e58e4620fa80ff9820f4f54bf185d86496f3456c
     description: >
       Small testing Measurement Set, stored on elwood's FTP server

where the `type` and `url` fields are self-explanatory and the `hash` field refers to
the `SHA256 <https://en.wikipedia.org/wiki/SHA-2_>`_ hash of the file to download.

Google drive entries contain a `file_id` field that uniquely identifies the file
for download from Google drive.

.. code:: yaml

   '/test/ms/2020-06-04/google/smallest_ms.tar.gz':
     type: google
     file_id: 1wjZoh7OAIVEjYuTmg9dLAFiLoyehnIcL
     hash: 9d6379b5ad01a1fe6ec218d4e58e4620fa80ff9820f4f54bf185d86496f3456c
     description: >
       Small testing Measurement Set, stored on Google Drive

Internally, this is translated into the following url:

.. code::

    https://drive.google.com/uc?export=download&id=1wjZoh7OAIVEjYuTmg9dLAFiLoyehnIcL



Creating a custom registry schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can define their own registry file containing custom entries.
It should be placed in ``$HOME/.config/packratt/registry.yaml``.
Each entry should refer to a single file. If one has a Measurement Set,
for example, one should tar and gzip the MS directory up

.. code:: bash

    $ tar cvfz WSRT.MS.tar.gz WSRT.MS/
    $ sha256sum WSRT.MS.tar.gz
    7cc6cfb657a1c495849e22f2f720bf1fd4555b106a5d7d23f91bd45cb460ae9a  WSRT.MS.tar.gz

Upload the tarfile to Google Drive or HTTPS/FTP server and create an entry in
the custom registry:

.. code:: yaml

    '/test/ms/2020-06-04/WSRT.MS.tar.gz':
        type: url
        url: ftp://www.ftp.com/pub/user/WSRT.tar.gz
        hash: 7cc6cfb657a1c495849e22f2f720bf1fd4555b106a5d7d23f91bd45cb460ae9a
        description: >
            My Measurement Set

This should now be available for download by packratt and for use
by an application:

.. code:: python

   import packratt
   import pytest

   def test_something(tmp_path_factory):
      # Create a temporary directory with pytest's tempory path utilities
      dest = tmp_path_factory.mktemp("ms")
      # Download file
      packratt.get('/test/ms/2020-06-04/WSRT.MS.tar.gz', dest)

      # Untar it
      with tarfile.open(dest / "WSRT.tar.gz") as tf:
         tf.extractall()

Contributing
------------

To contribute, please adhere to
`pep8 <https://www.python.org/dev/peps/pep-0008/>`__ coding standards

License
-------

`LICENSE <LICENSE>`__
