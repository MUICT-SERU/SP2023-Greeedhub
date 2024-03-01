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

from .utils import (
    WHEEL_EXTENSION, WHEEL_FILENAME_RE,
    match_egg_info_version, package_names_match, split_entry_ext,
    Endpoint, endpoint_from_url,
)


# Taken from distlib.compat (to match pip's implementation).
if sys.version_info < (3, 4):
    unescape = six.moves.html_parser.HTMLParser().unescape
else:
    from html import unescape


# These parsing helpers are bits and pieces collected from pip's HTMLPage
# and Link implementation.

def _parse_base_url(document):
    bases = [
        x for x in document.findall(".//base")
        if x.get("href") is not None
    ]
    if bases and bases[0].get("href"):
        return bases[0].get("href")
    return None


def _parse_name_version(filename, name):
    stem, ext = split_entry_ext(filename)
    if ext == WHEEL_EXTENSION:
        match = WHEEL_FILENAME_RE.match(filename)
        if not match:
            raise ValueError("invald wheel name {0!r}".format(filename))
        wheel_name, vers = match.group("name", "ver")
        if name is None:
            name = wheel_name
        elif not package_names_match(name, wheel_name):
            raise ValueError("invald wheel {0!r} for package {1!r}".format(
                filename, name,
            ))
    else:
        vers = match_egg_info_version(stem, name)
        if vers is None:
            raise ValueError("invalid filename {0!r}".format(filename))
        if name is None:
            name = stem[:-len(vers)]
            vers = vers[1:]     # Strip leading "-".
    return name, packaging.version.parse(vers)


CLEAN_URL_RE = re.compile(r'[^a-z0-9$&+,/:;=?@.#%_\\|-]', re.IGNORECASE)

HASH_RE = re.compile(r'(sha1|sha224|sha384|sha256|sha512|md5)=([a-f0-9]+)')


def _iter_entries(document, base_url, package_name):
    for anchor in document.findall(".//a"):
        href = anchor.get("href")
        if not href:
            continue
        try:
            package_name, version = _parse_name_version(
                anchor.text, package_name,
            )
        except ValueError:
            continue
        url = CLEAN_URL_RE.sub(
            lambda match: "%{:2x}".format(ord(match.group(0))),
            six.moves.urllib_parse.urljoin(base_url, href),
        )
        parsed_result = six.moves.urllib_parse.urlparse(url)
        hashes = dict(
            match.group(1, 2)
            for match in HASH_RE.finditer(parsed_result.fragment)
        )
        endpoint = endpoint_from_url(parsed_result)
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


def parse_from_html(html, base_url, package_name=None):
    """Parse entries from HTML source.

    `html` should be text of valid HTML 5 content. `package_name` should be
    the name of the package on this page, or `None` if not applicable.
    """
    document = html5lib.parse(html, namespaceHTMLElements=False)
    base_url = _parse_base_url(document) or base_url
    return list(_iter_entries(document, base_url, package_name))


def _entry_from_path(path):
    filename = os.path.basename(path)
    try:
        name, version = _parse_name_version(filename, None)
    except ValueError:
        return None
    return Entry(name, version, Endpoint(True, path), {}, None, None)


def list_from_paths(paths, root_directory):
    """Parse entries from a file listing.

    `paths` should be a sequence of paths, e.g. from `os.listdir()`. Paths can
    be either absolute or relative to `root_directory`.
    """
    return [
        entry for entry in (
            _entry_from_path(os.path.join(root_directory, path))
            for path in paths
        )
        if entry is not None
    ]
