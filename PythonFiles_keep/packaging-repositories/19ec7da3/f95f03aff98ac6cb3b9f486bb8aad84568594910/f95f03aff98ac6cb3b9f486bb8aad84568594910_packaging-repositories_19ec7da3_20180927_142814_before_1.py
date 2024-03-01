#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import collections
import os
import posixpath
import re

from packaging.utils import canonicalize_name
from six import string_types
from six.moves import urllib_parse, urllib_request


def package_names_match(a, b):
    if not isinstance(a, string_types) or not isinstance(b, string_types):
        return False
    return canonicalize_name(a) == canonicalize_name(b)


Endpoint = collections.namedtuple("Endpoint", "local value")


def endpoint_from_url(split_result):
    if split_result.scheme == "file":
        path = urllib_request.url2pathname(split_result.path)
        if split_result.netloc:     # UNC path.
            path = "\\\\{netloc}{path}".format(split_result.netloc, path)
        return Endpoint(True, path)
    defragged = split_result._replace(fragment="")
    return Endpoint(False, urllib_parse.urlunsplit(defragged))


def url_from_endpoint(endpoint):
    if not endpoint.local:
        return endpoint.value
    path = os.path.normpath(os.path.abspath(endpoint.value))
    return urllib_parse.urljoin("file:", urllib_request.pathname2url(path))


def split_entry_ext(path):
    """Like os.path.splitext, but take off .tar too.

    Taken from `pip._internal.utils.misc.splitext`.
    """
    base, ext = posixpath.splitext(path)
    if base.lower().endswith('.tar'):
        ext = base[-4:] + ext
        base = base[:-4]
    return base, ext


EGG_INFO_RE = re.compile(r"([a-z0-9_.]+)-([a-z0-9_.!+-]+)", re.IGNORECASE)


def match_egg_info_version(egg_info, search_name):
    """Pull the version part out of a string.

    Taken (simplified) from `pip._internal.index.egg_info_matches`.

    :param egg_info: The string to parse. E.g. foo-2.1
    :param search_name: The name of the package this belongs to.
    """
    match = EGG_INFO_RE.search(egg_info)
    if not match:
        return None
    name = match.group(0).lower()
    # To match the "safe" name that pkg_resources creates:
    name = name.replace('_', '-')
    # project name and version must be separated by a dash
    look_for = search_name.lower() + "-"
    if name.startswith(look_for):
        return match.group(0)[len(look_for):]
    return None


# Taken from `pip._internal.wheel.Wheel.wheel_file_re`.
WHEEL_FILENAME_RE = re.compile(
    r"""^(?P<namever>(?P<name>.+?)-(?P<ver>.*?))
    ((-(?P<build>\d[^-]*?))?-(?P<pyver>.+?)-(?P<abi>.+?)-(?P<plat>.+?)
    \.whl|\.dist-info)$""",
    re.VERBOSE,
)


# Taken from `pip._internal.Wheel.wheel_ext`.
WHEEL_EXTENSION = ".whl"


def guess_encoding(headers):
    """Guess transport encoding from response headers.

    Taken from `pip._internal.index.HTMLPage`.

    We don't use this, but this is extremely useful when implementing fetchers,
    why not supply it to avoid duplication.
    """
    if headers and "Content-Type" in headers:
        content_type, params = cgi.parse_header(headers["Content-Type"])
        if "charset" in params:
            return params["charset"]
    return None
