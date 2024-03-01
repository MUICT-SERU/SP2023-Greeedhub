#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os

import aiohttp

from packaging.requirements import Requirement
from packaging_repositories import Fetcher, SimpleRepository


async def iter_all_entries(fetcher):
    # FIXME: This isn't really doing anything concurrently.
    async with aiohttp.ClientSession() as session:
        for endpoint in fetcher.repository.iter_endpoints(fetcher.requirement):
            if endpoint.local:
                path = endpoint.value
                if os.path.isdir(path):
                    src = [os.path.join(path, n) for n in os.listdir(path)]
                else:
                    with open(path, encoding="utf-8") as f:
                        src = f.read()
            else:
                async with session.get(endpoint.value) as response:
                    response.raise_for_status()
                    src = await response.text()
            for entry in fetcher.iter_entries(endpoint, src):
                yield entry


class AIOHTTPFetcher(Fetcher):
    """Fetcher implementation using AIOHTTP to make HTTP(S) requests.
    """
    def __init__(self, *args, **kwargs):
        super(AIOHTTPFetcher, self).__init__(*args, **kwargs)
        self._iterator = iter_all_entries(self)

    def __anext__(self):
        return self._iterator.__anext__()


async def fetch(repository, requirement):
    fetcher = AIOHTTPFetcher(repository, requirement)
    entries = []
    async for entry in fetcher:
        entries.append(entry)
    return entries


def test_basic():
    pypi = SimpleRepository("https://pypi.org/simple")
    entries = asyncio.run(fetch(pypi, Requirement("pip>=9,<10")))
    assert len(entries) >= 8, entries
