#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from .utils import package_names_match


def _is_match(entry, requirement, environment):
    if not package_names_match(entry.name, requirement.name):
        return False
    specifier = requirement.specifier
    if specifier and not specifier.contains(entry.version):
        return False
    marker = requirement.marker
    if marker and not marker.evaluate(environment):
        return False
    return True


class Fetcher(object):
    """Base fetch implementation to apply requirement filtering.
    """
    def __init__(self, repository, requirement, environment=None):
        self._repository = repository
        self._requirement = requirement
        self._environment = environment

    def __repr__(self):
        parts = [
            repr(self._repository.endpoint.value),
            repr(str(self._requirement)),
        ]
        if self._environment:
            parts.append(repr(self._environment))
        return "Fetcher({0})".format(", ".join(parts))

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    if six.PY2:
        def next(self):
            return self.__next__()

    def iter_endpoints(self):
        for endpoint in self._repository.iter_endpoints(self._requirement):
            yield endpoint

    def iter_entries(self, endpoint, source):
        for entry in self._repository.get_entries(endpoint, source):
            if _is_match(entry, self._requirement, self._environment):
                yield entry
