#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import six


class Endpoint(object):
    """Data class to represent an identifier to a thing.

    This has two variants: local or nonlocal. A local endpoint's `value` would
    be a path on the local filesystem; a nonlocal one's would be a URL.

    The distinction is useful when deciding how the identified thing should
    be accessed, e.g. by an HTTP library such as Requests, or directly with
    `open()` or `os.listdir()`.
    """
    __slots__ = ("local", "value")

    def __init__(self, local, value):
        self.local = local
        self.value = value

    def __repr__(self):
        return "Endpoint(local={local!r}, value={value!r})".format(
            local=self.local, value=self.value,
        )

    def __eq__(self, other):
        if not isinstance(other, Endpoint):
            return NotImplemented
        return self.local == other.local and self.value == other.value

    @classmethod
    def from_url(cls, url):
        if not isinstance(url, tuple):
            url = six.moves.urllib.parse.urlsplit(url)
        if url.scheme == "file":
            path = six.moves.urllib.request.url2pathname(url.path)
            if url.netloc:  # UNC path.
                path = "\\\\{netloc}{path}".format(url.netloc, path)
            return cls(True, path)
        defragged = url._replace(fragment="")
        return cls(False, six.moves.urllib.parse.urlunsplit(defragged))

    def as_url(self):
        if not self.local:
            return self.value
        path = os.path.normpath(os.path.abspath(self.value))
        return six.moves.urllib.parse.urljoin(
            "file:", six.moves.urllib.request.pathname2url(path),
        )

    def _replace(self, **kwargs):
        return Endpoint(**{
            key: kwargs.get(key, getattr(self, key))
            for key in self.__slots__
        })
