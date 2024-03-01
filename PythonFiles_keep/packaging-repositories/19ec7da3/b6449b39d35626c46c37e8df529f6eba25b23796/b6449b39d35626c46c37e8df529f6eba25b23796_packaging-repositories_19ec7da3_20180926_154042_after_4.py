#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from .utils import package_names_match


class Fetcher(six.Iterator):
    """Base fetch implementation to apply requirement filtering.
    """
    def __init__(self, repository, package_name):
        self._repository = repository
        self._package_name = package_name

    def __repr__(self):
        return "Fetcher({endpoint!r}, {package_name!r})".format(
            endpoint=self._repository.base_endpoint.value,
            package_name=self._package_name,
        )

    def __iter__(self):
        return self

    def __aiter__(self):
        return self

    def iter_endpoints(self):
        for endpoint in self._repository.iter_endpoints(self._package_name):
            yield endpoint

    def iter_entries(self, endpoint, source):
        for entry in self._repository.get_entries(endpoint, source):
            if package_names_match(entry.name, self._package_name):
                yield entry
