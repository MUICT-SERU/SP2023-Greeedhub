#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections


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


def parse_from_html(html):
    """Parse entries from HTML source.

    `html` should be text of valid HTML 5 content.
    """
    raise NotImplementedError("TODO")


def list_from_paths(paths):
    """Parse entries from HTML source.

    `paths` should be a sequence of *absolute* paths.
    """
    raise NotImplementedError("TODO")
