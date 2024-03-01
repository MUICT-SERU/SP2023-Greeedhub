#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import posixpath

from packaging.utils import canonicalize_name
from six.moves import urllib_parse, urllib_request

from .entries import list_from_paths, parse_from_html


def _is_filesystem_path(parsed_result):
    if not parsed_result.scheme:
        return True
    if len(parsed_result.scheme) > 1:
        return False
    # urlparse misidentifies Windows absolute paths. In this situation, the
    # scheme would be a single letter (drive name), and netloc would be empty.
    if not parsed_result.netloc:
        return True
    return False


Endpoint = collections.namedtuple("Endpoint", "local value")


class _Repository(object):

    def __init__(self, endpoint):
        self._base_endpoint = endpoint

    def __repr__(self):
        return "{0}({1!r})".format(type(self).__name__, self.endpoint.value)

    @property
    def base_endpoint(self):
        endpoint = self._base_endpoint
        parsed_result = urllib_parse.urlparse(endpoint)
        if _is_filesystem_path(parsed_result):
            return Endpoint(True, endpoint)
        if parsed_result.scheme == "file":
            return Endpoint(True, urllib_request.url2pathname(endpoint).path)
        defragged_result = parsed_result._replace(fragment="")
        return Endpoint(False, urllib_parse.urlunparse(defragged_result))


class SimpleRepository(_Repository):
    """A repository compliant to PEP 503 "Simple Repository API".
    """
    def iter_endpoints(self, requirement):
        name = canonicalize_name(requirement.name)
        base_endpoint = self.base_endpoint
        value = posixpath.join(base_endpoint.value, name, "")
        yield base_endpoint._replace(value=value)

    def get_entries(self, endpoint, html):
        return parse_from_html(endpoint.value, html)


class FlatHTMLRepository(_Repository):
    """A repository represented by a single HTML file.

    This is the non-directory variant of pip's --find-links.
    """
    def iter_endpoints(self, requirement):
        yield self.base_endpoint

    def get_entries(self, endpoint, html):
        return parse_from_html(None, html)


class LocalDirectoryRepository(_Repository):
    """A repository represented by a directory on the local filesystem.

    This is the directory variant of pip's --find-links.
    """
    def __init__(self, endpoint):
        super(LocalDirectoryRepository, self).__init__(endpoint)
        if not self.base_endpoint.local:
            raise ValueError("endpoint is not local")

    def iter_endpoints(self, requirement):
        yield self.base_endpoint

    def get_entries(self, endpoint, paths):
        return list_from_paths(endpoint, paths)
