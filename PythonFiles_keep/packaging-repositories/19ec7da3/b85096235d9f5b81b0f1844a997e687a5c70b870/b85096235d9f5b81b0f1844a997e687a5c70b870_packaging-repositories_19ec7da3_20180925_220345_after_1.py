#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import os

import packaging.specifiers
import packaging.version
import six

from .utils import (
    WHEEL_EXTENSION, WHEEL_FILENAME_RE,
    match_egg_info_version, package_names_match, split_entry_ext,
)


Entry = collections.namedtuple("Entry", [
    "name",             # Name of the project. Not necessarily canonical?
    "version",          # packaging.version.
    "location",         # URL or path to get the file.
    "hashes",           # Mapping of hashes, {hashname: hexdigest}.
    "requires_python",  # packaging.specifiers.SpecifierSet or None.
    "gpg_sig",          # str or None.
])
"""A downloadable thing in a repository.

This would be an anchor tag in an HTML file, or a file in a directory.
"""


def _parse_name_version(filename, name):
    stem, ext = split_entry_ext(filename)
    if ext == WHEEL_EXTENSION:
        match = WHEEL_FILENAME_RE.match(filename)
        if not match:
            raise ValueError("invald wheel name {0!r}".format(filename))
        wheel_name, vers = match.group("name", "ver")
        if name is not None and not package_names_match(name, wheel_name):
            raise ValueError("invald wheel {0!r} for package {1!r}".format(
                filename, name,
            ))
    else:
        vers = match_egg_info_version(stem, name)
        if vers is None:
            raise ValueError("invalid filename {0!r}".format(filename))
        if name is None:
            suffix_len = len(vers) + 1  # Strip version and the dash before it.
            name = stem[:-suffix_len]
    return name, packaging.version.parse(vers)


class SimplePageParser(six.moves.html_parser.HTMLParser):
    """Parser to scrap links from a simple API page.
    """
    def __init__(self, base_url):
        # Can't use super() because HTMLParser was an old-style class.
        six.moves.html_parser.HTMLParser.__init__(self)
        self.base_url_parts = six.moves.urllib_parse.urlsplit(base_url)
        self.name = base_url.rstrip("/").rsplit("/", 1)[-1]
        self.current_a_data = None
        self.entries = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        url_parts = None
        hashes = {}
        requires_python = None
        gpg_sig = None
        for attr, value in attrs:
            if attr == "href":
                url_parts = six.moves.urllib_parse.urlsplit(value)
                if url_parts.fragment:
                    htype, hvalue = url_parts.fragment.split("=", 1)
                    url_parts = url_parts._replace(fragment="")
                    hashes[htype] = hvalue
                replacements = {
                    fn: part
                    for fn, part in zip(url_parts._fields, url_parts)
                    if part and fn != "fragment"
                }
                replacements["fragment"] = ""
                url_parts = self.base_url_parts._replace(**replacements)
            elif attr == "data-requires-python":
                requires_python = packaging.specifiers.SpecifierSet(value)
            elif attr == "data-gpg-sig":
                gpg_sig = value
        if url_parts:
            url = six.moves.urllib_parse.urlunsplit(url_parts)
            self.current_a_data = (url, hashes, requires_python, gpg_sig)

    def handle_endtag(self, tag):
        if tag.lower() != "a":
            return
        self.current_a_data = None

    def handle_data(self, data):
        if self.current_a_data is None:
            return
        try:
            _, version = _parse_name_version(data, self.name)
        except ValueError:
            return
        self.entries.append(Entry(self.name, version, *self.current_a_data))


def parse_from_html(url, html):
    """Parse entries from HTML source.

    `url` should be the simple API URL, or None if not applicable. `html`
    should be text of valid HTML 5 content.
    """
    parser = SimplePageParser(url)
    parser.feed(html)
    return parser.entries


def _entry_from_path(path):
    filename = os.path.basename(path)
    try:
        name, version = _parse_name_version(filename, None)
    except ValueError:
        return None
    return Entry(name, version, path, {}, None, None)


def list_from_paths(directory, paths):
    """Parse entries from HTML source.

    `paths` should be a sequence of paths, e.g. from `os.listdir()`. Paths can
    be either absolute or relative to `directory`.
    """
    return [
        entry for entry in (
            _entry_from_path(os.path.join(directory, path))
            for path in paths
        )
        if entry is not None
    ]
