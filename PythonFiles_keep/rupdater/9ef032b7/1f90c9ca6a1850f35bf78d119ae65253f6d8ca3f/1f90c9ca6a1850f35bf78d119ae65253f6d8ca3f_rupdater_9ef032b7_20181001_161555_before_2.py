#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# rupdater - lightweight dependency free update software
# Copyright (C) 2018  Ranx

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import hashlib
import json
import re
import tempfile
import urllib.request
from contextlib import contextmanager
from distutils.version import StrictVersion


class Updater:
    def __init__(self, current_version, version_data_url, use_json=False):
        """Create new Updater instance.

        Args:
            current_version (str): Current version of your software.
            version_data_url (str): URL of the version data file.
            use_json (Optional[bool]): Does version data file formatted as JSON (requires jsonschema).
        """
        self.current_version = StrictVersion(current_version)
        self.remote_version = None
        self.version_data_url = version_data_url
        self.remote_file_url = None
        self.hash_algo = None
        self.hash = None
        self.use_json = use_json

    def get_version_data(self):
        """Extract version data from file by given URL.

        Raises:
            ValueError: If version data is incorrect.

        """
        with urllib.request.urlopen(self.version_data_url, timeout=10) as req:
            version_data = bytearray()
            [version_data.extend(chunk) for chunk in iter(lambda: req.read(1024 * 16), b'')]
            url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b' \
                          r'(?:[-a-zA-Z0-9@:%_+.~#?&/=]*)'
            if self.use_json:
                version_json = json.loads(version_data)

                # validate the structure of version data file
                if not all(k in version_json for k in ('remote_version', 'remote_file_url', 'hash_algo', 'hash')):
                    raise ValueError('incorrect version data file (missing property)')
                p = re.compile('^{}$'.format(url_pattern))
                if not p.match(version_json['remote_file_url']):  # is URL valid
                    raise ValueError('incorrect remote_file_url')
                if not version_json['hash_algo'] in hashlib.algorithms_guaranteed:
                    raise ValueError('unknown hashing algorithm')

                self.remote_version = StrictVersion(version_json['remote_version'])
                self.remote_file_url = version_json['remote_file_url']
                self.hash_algo = version_json['hash_algo']
                self.hash = version_json['hash'].lower()
            else:
                p = re.compile(r'(.+)#({})#({})#([0-9a-fA-F]+)'
                               .format(url_pattern, '|'.join(hashlib.algorithms_guaranteed)))
                m = p.match(version_data.decode('utf-8'))
                if m is not None:
                    self.remote_version = StrictVersion(m.group(1))
                    self.remote_file_url = m.group(2)
                    self.hash_algo = m.group(3)
                    self.hash = m.group(4).lower()
                else:
                    raise ValueError('incorrect version data file')

    def check(self):
        """Compare local and remote versions of the software.

        Returns:
            bool: Was update found.

        """
        self.get_version_data()
        return self.current_version < self.remote_version

    @contextmanager
    def download(self, chunk_size=1024 * 16):
        """Download an update.

        Warning: use only with context manager (``with`` statement, like ``open`` function).

        Args:
            chunk_size (Optional[int]): Size of a one chunk.

        Returns:
            file: Update file.

        Examples:
            >>> with updater.download() as update_file:

        """
        tmp_file = tempfile.NamedTemporaryFile()
        try:
            if self.remote_file_url is not None:
                with urllib.request.urlopen(self.remote_file_url) as req:
                    [tmp_file.write(chunk) for chunk in iter(lambda: req.read(chunk_size), b'')]
                    tmp_file.seek(0)
            yield tmp_file
        finally:
            tmp_file.close()

    @staticmethod
    def hash_file(f, hash_algo, chunk_size=1024 * 16):
        """Get hash sum of the file.

        Args:
            f (file): File to hash.
            hash_algo (str): Hashing algorithm.
            chunk_size (Optional[int]): Size of a one chunk.

        Returns:
            str: Hash sum of the file.

        Raises:
            ValueError: If unknown hashing algorithm was given.

        """
        if hash_algo not in hashlib.algorithms_guaranteed:
            raise ValueError('can not find hashing algorithm: {}'.format(hash_algo))
        hasher = getattr(hashlib, hash_algo)()
        [hasher.update(chunk) for chunk in iter(lambda: f.read(chunk_size), b'')]
        return hasher.hexdigest()
