#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

import requests

from packaging.requirements import Requirement
from packaging_repositories import Fetcher, SimpleRepository


def iter_entries(fetcher):
    session = requests.session()
    for endpoint in fetcher.repository.iter_endpoints(fetcher.requirement):
        if endpoint.local:
            path = endpoint.value
            if os.path.isdir(path):
                src = [os.path.join(path, name) for name in os.listdir(path)]
            else:
                with io.open(path, encoding="utf-8") as f:
                    src = f.read()
        else:
            response = session.get(endpoint.value)
            response.raise_for_status()
            src = response.text
        for entry in fetcher.iter_entries(src):
            if fetcher.match(entry):
                yield entry


class RequestsFetcher(Fetcher):
    """Fetcher implementation using Requests to make HTTP(S) requests.
    """
    def __init__(self, *args, **kwargs):
        super(RequestsFetcher, self).__init__(*args, **kwargs)
        self._iterator = iter_entries(self)

    def __next__(self):
        return next(self._iterator)


def test_basic():
    pypi = SimpleRepository("https://pypi.org/simple")
    fetcher = RequestsFetcher(pypi, Requirement("pip>=9,<10"))
    entries = list(fetcher)
    assert len(entries) >= 8
