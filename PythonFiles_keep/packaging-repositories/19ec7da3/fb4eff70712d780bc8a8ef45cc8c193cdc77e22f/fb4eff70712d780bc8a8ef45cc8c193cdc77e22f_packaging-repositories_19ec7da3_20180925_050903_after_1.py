#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import os

import packaging.version

from .utils import (
    WHEEL_EXTENSION, WHEEL_FILENAME_RE,
    match_egg_info_version, split_entry_ext,
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
        return match.group("name", "ver")
    vers = match_egg_info_version(stem, name)
    version = packaging.version.parse(vers)
    if name is None:
        suffix_len = len(vers) + 1  # Strip version and the dash before it.
        name = stem[:-suffix_len]
    return name, version


def parse_from_html(name, html):
    """Parse entries from HTML source.

    `name` should be the package name, or None if not applicable. `html`
    should be text of valid HTML 5 content.
    """
    raise NotImplementedError("TODO")


def _entry_from_path(path):
    filename = os.path.basename(path)
    name, version = _parse_name_version(filename, None)
    return Entry(name, version, path, {}, None, None)


def list_from_paths(directory, paths):
    """Parse entries from HTML source.

    `paths` should be a sequence of paths, e.g. from `os.listdir()`. Paths can
    be either absolute or relative to `directory`.
    """
    return [_entry_from_path(os.path.join(directory, path)) for path in paths]
