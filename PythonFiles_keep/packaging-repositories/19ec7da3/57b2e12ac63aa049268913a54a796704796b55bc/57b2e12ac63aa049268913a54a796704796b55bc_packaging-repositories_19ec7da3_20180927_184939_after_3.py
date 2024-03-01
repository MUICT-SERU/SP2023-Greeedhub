#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import os
import sys
import re

import html5lib
import packaging.specifiers
import packaging.version
import six

from .endpoints import Endpoint
from .utils import (
    WHEEL_EXTENSION, WHEEL_FILENAME_RE,
    match_egg_info_version, package_names_match, split_entry_ext,
)


# Taken from distlib.compat (to match pip's implementation).
if sys.version_info < (3, 4):
    unescape = six.moves.html_parser.HTMLParser().unescape
else:
    from html import unescape


# These parsing helpers are bits and pieces collected from pip's HTMLPage
# and Link implementation.

def _parse_base_url(document, transport_url):
    bases = [
        x for x in document.findall(".//base")
        if x.get("href") is not None
    ]
    if not bases:
        return transport_url
    parsed_url = bases[0].get("href")
    if parsed_url:
        return parsed_url
    return transport_url


def _parse_version(filename, package_name):
    stem, ext = split_entry_ext(filename)
    if ext == WHEEL_EXTENSION:
        match = WHEEL_FILENAME_RE.match(filename)
        if not match:
            raise ValueError("invald wheel name {0!r}".format(filename))
        wheel_name, vers = match.group("name", "ver")
        if not package_names_match(package_name, wheel_name):
            raise ValueError("invald wheel {0!r} for package {1!r}".format(
                filename, package_name,
            ))
    else:
        vers = match_egg_info_version(stem, package_name)
        if vers is None:
            raise ValueError("invalid filename {0!r}".format(filename))
    return packaging.version.parse(vers)


CLEAN_URL_RE = re.compile(r'[^a-z0-9$&+,/:;=?@.#%_\\|-]', re.IGNORECASE)

HASH_RE = re.compile(r'(sha1|sha224|sha384|sha256|sha512|md5)=([a-f0-9]+)')


def _iter_entries(document, base_url, package_name):
    for anchor in document.findall(".//a"):
        href = anchor.get("href")
        if not href:
            continue
        try:
            version = _parse_version(anchor.text, package_name)
        except ValueError:
            continue
        url = CLEAN_URL_RE.sub(
            lambda match: "%{:2x}".format(ord(match.group(0))),
            six.moves.urllib_parse.urljoin(base_url, href),
        )
        split_result = six.moves.urllib_parse.urlsplit(url)
        hashes = dict(
            match.group(1, 2)
            for match in HASH_RE.finditer(split_result.fragment)
        )
        endpoint = Endpoint.from_url(split_result)
        requires_python = packaging.specifiers.SpecifierSet(
            unescape(anchor.get("data-requires-python", "")),
        )
        gpg_sig = unescape(anchor.get("data-gpg-sig", ""))
        yield Entry(
            package_name, version, endpoint,
            hashes, requires_python, gpg_sig,
        )


Entry = collections.namedtuple("Entry", [
    "name",             # Name of the project. Not necessarily canonical?
    "version",          # packaging.version._BaseVersion.
    "endpoint",         # Endpoint to get the file.
    "hashes",           # Mapping of hashes, {hashname: hexdigest}.
    "requires_python",  # packaging.specifiers.SpecifierSet.
    "gpg_sig",          # str, maybe empty.
])
"""A downloadable thing in a repository.

This would be an anchor tag in an HTML file, or a file in a directory.
"""


def parse_from_html(html, page_url, package_name):
    """Parse entries from HTML source.

    `html` should be valid HTML 5 content. This could be either text, or a
    2-tuple of (content, encoding). In the latter case, content would be
    binary, and the encoding is passed into html5lib as transport encoding to
    guess the document's encoding. The transport encoding can be `None` if
    the callee does not have this information.

    `package_name` should be the name of the package on this page.
    """
    kwargs = {"namespaceHTMLElements": False}
    if not isinstance(html, six.string_types):
        html, kwargs["transport_encoding"] = html
    document = html5lib.parse(html, **kwargs)
    base_url = _parse_base_url(document, page_url)
    return list(_iter_entries(document, base_url, package_name))


def _entry_from_path(path, package_name):
    filename = os.path.basename(path)
    try:
        version = _parse_version(filename, package_name)
    except ValueError:
        return None
    return Entry(package_name, version, Endpoint(True, path), {}, None, None)


def list_from_paths(paths, root, package_name):
    """Parse entries from a file listing.

    `paths` should be a sequence of paths, e.g. from `os.listdir()`. Paths can
    be either absolute or relative to `root`.
    """
    return [
        entry for entry in (
            _entry_from_path(os.path.join(root, path), package_name)
            for path in paths
        )
        if entry is not None
    ]
