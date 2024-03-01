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
import re
import tempfile
import urllib.request
from contextlib import contextmanager
from distutils.version import StrictVersion


class Updater:
    def __init__(self, current_version, version_data_url):
        """Updater

        :param current_version: Current version of the software
        :param version_data_url: URL of the version data file
        """
        self.current_version = StrictVersion(current_version)
        self.remote_version = None
        self.version_data_url = version_data_url
        self.remote_file_url = None
        self.hash_algo = None
        self.hash = None

    def get_version_data(self):
        with urllib.request.urlopen(self.version_data_url, timeout=10) as req:
            p = re.compile(r'(.+)#(https?://(?:www\.)?'
                           r'[-a-zA-Z0-9@:%._+~#=]{{2,256}}\.[a-z]{{2,6}}\b(?:[-a-zA-Z0-9@:%_+.~'
                           r'#?&/=]*))#({})#([0-9a-fA-F]+)'.format('|'.join(hashlib.algorithms_guaranteed)))
            m = p.match(req.read().decode('utf-8'))
            if m is not None:
                self.remote_version = StrictVersion(m.group(1))
                self.remote_file_url = m.group(2)
                self.hash_algo = m.group(3)
                self.hash = m.group(4).lower()
            else:
                raise ValueError('incorrect version data file')

    def check(self):
        self.get_version_data()
        return self.current_version < self.remote_version

    @contextmanager
    def download(self, chunk_size=1024 * 16):
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
        if hash_algo not in hashlib.algorithms_guaranteed:
            raise ValueError('could not found hashing algorithm: {}'.format(hash_algo))
        hasher = getattr(hashlib, hash_algo)()
        [hasher.update(chunk) for chunk in iter(lambda: f.read(chunk_size), b'')]
        return hasher.hexdigest()
