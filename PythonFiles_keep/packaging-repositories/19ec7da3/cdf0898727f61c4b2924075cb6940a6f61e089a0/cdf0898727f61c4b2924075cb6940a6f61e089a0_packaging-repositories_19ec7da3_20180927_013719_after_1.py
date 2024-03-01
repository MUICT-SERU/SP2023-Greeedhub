#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

import pytest

import requests

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from packaging_repositories import (
    Endpoint, Entry, Fetcher,
    FlatHTMLRepository, SimpleRepository, VersionFilter,
)


def iter_all_entries(fetcher):
    session = requests.session()
    for endpoint in fetcher.iter_endpoints():
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
        for entry in fetcher.iter_entries(endpoint, src):
            yield entry


class RequestsFetcher(Fetcher):
    """Fetcher implementation using Requests to make HTTP(S) requests.
    """
    def __init__(self, *args, **kwargs):
        super(RequestsFetcher, self).__init__(*args, **kwargs)
        self._iterator = iter_all_entries(self)

    def __next__(self):
        return next(self._iterator)


def test_simple():
    pypi = SimpleRepository("https://pypi.org/simple")
    fetcher = RequestsFetcher(pypi, "pip")
    version_filter = VersionFilter(">=9,<10")
    entries = list(version_filter(fetcher))
    assert len(entries) == 8, entries


def get_data(name):
    return os.path.join(os.path.dirname(__file__), "data", name)


@pytest.fixture()
def flat_repo():
    repo = FlatHTMLRepository(get_data("links.html"))
    return repo


def test_flat_nomatch(flat_repo):
    fetcher = RequestsFetcher(flat_repo, "pip")
    entries = list(fetcher)
    assert len(entries) == 0, entries


def test_flat_match(flat_repo):
    fetcher = RequestsFetcher(flat_repo, "jinja2")
    entries = list(fetcher)
    assert entries == [
        Entry(
            name="jinja2", version=Version("2.10"),
            endpoint=Endpoint(
                local=True,
                value=get_data("Jinja2-2.10-py2.py3-none-any.whl"),
            ),
            hashes={}, requires_python=SpecifierSet(), gpg_sig=""),
    ]


def test_flat_match_filter(flat_repo):
    fetcher = RequestsFetcher(flat_repo, "jinja2")
    assert len(list(VersionFilter("~=2.0")(fetcher))) == 1


def test_flat_match_filter_nomatch(flat_repo):
    fetcher = RequestsFetcher(flat_repo, "jinja2")
    assert len(list(VersionFilter(">2.10")(fetcher))) == 0
