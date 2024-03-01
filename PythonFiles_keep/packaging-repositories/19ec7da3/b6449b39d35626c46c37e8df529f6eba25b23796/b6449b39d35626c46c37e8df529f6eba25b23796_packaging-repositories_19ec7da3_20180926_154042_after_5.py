#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import packaging.specifiers
import packaging.version
import six


ASYNC_ITERATOR_CODE = """
def __aiter__(self):
    return self

async def __anext__(self):
    while True:
        value = await self.iterator.__anext__()
        if self.func(value):
            return value
"""


class _Filter(six.Iterator):
    """Implement both sync and async iterator protocols.

    This is used internally as the return value of ``Filter.__call__()``.
    """
    def __init__(self, func, iterator):
        self.func = func
        self.iterator = iterator

    def __repr__(self):
        return "_Filter({0}, {1})".format(self.func, self.iterator)

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            value = next(self.iterator)
            if self.func(value):
                return value

    if sys.version_info >= (3, 6):
        six.exec_(ASYNC_ITERATOR_CODE)


class Filter(object):
    """Base class for an entry filter.

    This class does not do anything. Subclasses are expected to override
    ``match`` to perform the actual filtering logic.
    """
    def __call__(self, entry_iterator):
        return _Filter(self.match, entry_iterator)

    def match(self, entry):
        return True


class RequiresPythonFilter(Filter):
    """Filter on the requires-python specifier matching the given version.
    """
    def __init__(self, version):
        if isinstance(version, six.string_types):
            version = packaging.version.parse(version)
        self.version = version

    def __repr__(self):
        return "RequiresPythonFilter({0!r})".format(str(self.version))

    def match(self, entry):
        return entry.requires_python.contains(self.version)


class VersionFilter(Filter):
    """Filter on the version contained in a given range.
    """
    def __init__(self, specifier):
        if isinstance(specifier, six.string_types):
            specifier = packaging.specifiers.SpecifierSet(specifier)
        self.specifier = specifier

    def __repr__(self):
        return "VersionFilter({0!r})".format(str(self.specifier))

    def match(self, entry):
        return self.specifier.contains(entry.version)
