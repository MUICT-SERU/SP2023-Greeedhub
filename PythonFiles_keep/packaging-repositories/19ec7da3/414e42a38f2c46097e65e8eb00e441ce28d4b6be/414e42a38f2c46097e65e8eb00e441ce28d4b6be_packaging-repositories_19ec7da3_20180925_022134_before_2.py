#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import posixpath

from packaging.utils import canonicalize_name
from six.moves import urllib_parse, urllib_request


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
    def endpoint(self):
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
    def get_endpoint(self, requirement):
        name = canonicalize_name(requirement.name)
        value = posixpath.join(self.endpoint.value, name, "")
        return self.endpoint._replace(value=value)


class FlatRepository(_Repository):
    """A "flat" repository, as implemented by pip's --find-links.

    This could be
    """
    def get_endpoint(self, requirement):
        return self.endpoint
