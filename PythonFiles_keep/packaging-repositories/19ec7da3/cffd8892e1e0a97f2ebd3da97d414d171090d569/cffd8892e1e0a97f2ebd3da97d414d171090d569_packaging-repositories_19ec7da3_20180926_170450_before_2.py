#!/usr/bin/env python
# -*- coding: utf-8 -*-

import posixpath
import re

from packaging.utils import canonicalize_name


def package_names_match(a, b):
    return canonicalize_name(a) == canonicalize_name(b)


def split_entry_ext(path):
    """Like os.path.splitext, but take off .tar too.

    Taken from `pip._internal.utils.misc.splitext`.
    """
    base, ext = posixpath.splitext(path)
    if base.lower().endswith('.tar'):
        ext = base[-4:] + ext
        base = base[:-4]
    return base, ext


EGG_INFO_RE = re.compile(r'([a-z0-9_.]+)-([a-z0-9_.!+-]+)', re.I)


def match_egg_info_version(egg_info, search_name, _egg_info_re=EGG_INFO_RE):
    """Pull the version part out of a string.

    Taken from `pip._internal.index.egg_info_matches`.

    :param egg_info: The string to parse. E.g. foo-2.1
    :param search_name: The name of the package this belongs to. None to
        infer the name. Note that this cannot unambiguously parse strings
        like foo-2-2 which might be foo, 2-2 or foo-2, 2.
    :param link: The link the string came from, for logging on failure.
    """
    match = _egg_info_re.search(egg_info)
    if not match:
        return None
    if search_name is None:
        full_match = match.group(0)
        return full_match[full_match.index('-'):]
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
    re.VERBOSE
)


# Taken from `pip._internal.Wheel.wheel_ext`.
WHEEL_EXTENSION = ".whl"
