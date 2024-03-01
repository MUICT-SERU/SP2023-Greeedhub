#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import posixpath

from packaging.utils import canonicalize_name
from six.moves import urllib_parse

from .entries import list_from_paths, parse_from_html
from .utils import Endpoint, endpoint_from_url, url_from_endpoint


def _is_filesystem_path(split_result):
    if not split_result.scheme:
        return True
    if len(split_result.scheme) > 1:
        return False
    # urlparse misidentifies Windows absolute paths. In this situation, the
    # scheme would be a single letter (drive name), and netloc would be empty.
    if not split_result.netloc:
        return True
    return False


class _Repository(object):

    def __init__(self, endpoint):
        self._base_endpoint = endpoint

    def __repr__(self):
        return "{name}({endpoint!r})".format(
            name=type(self).__name__, endpoint=self.base_endpoint.value,
        )

    @property
    def base_endpoint(self):
        endpoint = self._base_endpoint
        split_result = urllib_parse.urlsplit(endpoint)
        if _is_filesystem_path(split_result):
            return Endpoint(True, os.path.normpath(os.path.abspath(endpoint)))
        return endpoint_from_url(split_result)


class SimpleRepository(_Repository):
    """A repository compliant to PEP 503 "Simple Repository API".
    """
    def iter_endpoints(self, package_name):
        name = canonicalize_name(package_name)
        base_endpoint = self.base_endpoint
        value = posixpath.join(base_endpoint.value, name, "")
        yield base_endpoint._replace(value=value)

    def get_entries(self, package_name, endpoint, html):
        return parse_from_html(html, url_from_endpoint(endpoint), package_name)


class FlatHTMLRepository(_Repository):
    """A repository represented by a single HTML file.

    This is the non-directory variant of pip's --find-links.
    """
    def iter_endpoints(self, package_name):
        yield self.base_endpoint

    def get_entries(self, package_name, endpoint, html):
        return parse_from_html(html, url_from_endpoint(endpoint), package_name)


class LocalDirectoryRepository(_Repository):
    """A repository represented by a directory on the local filesystem.

    This is the directory variant of pip's --find-links.
    """
    def __init__(self, endpoint):
        super(LocalDirectoryRepository, self).__init__(endpoint)
        if not self.base_endpoint.local:
            raise ValueError("endpoint is not local")

    def iter_endpoints(self, package_name):
        yield self.base_endpoint

    def get_entries(self, package_name, endpoint, paths):
        return list_from_paths(paths, endpoint.value, package_name)
