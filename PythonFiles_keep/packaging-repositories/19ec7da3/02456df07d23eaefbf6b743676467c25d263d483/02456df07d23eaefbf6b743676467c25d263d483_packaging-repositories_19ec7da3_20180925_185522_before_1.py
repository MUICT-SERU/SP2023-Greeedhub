#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os

import aiohttp

from packaging.requirements import Requirement
from packaging_repositories import Fetcher, SimpleRepository


def as_future(value):
    future = asyncio.Future()
    future.set_result(value)
    return future


async def read_remote_text(session, url):
    response = await session.get(url)
    response.raise_for_status()
    return (await response.text())


async def iter_futures(session, fetcher):
    for endpoint in fetcher.repository.iter_endpoints(fetcher.requirement):
        if endpoint.local:
            path = endpoint.value
            if os.path.isdir(path):
                names = [os.path.join(path, n) for n in os.listdir(path)]
                yield endpoint, as_future(names)
            else:
                with open(path, encoding="utf-8") as f:
                    yield endpoint, as_future(f.read())
        else:
            coro = read_remote_text(session, endpoint.value)
            yield endpoint, asyncio.ensure_future(coro)


async def iter_all_entries(fetcher):
    async with aiohttp.ClientSession() as session:
        future_endpoints = {
            future: endpoint
            async for endpoint, future in iter_futures(session, fetcher)
        }
        pending = set(future_endpoints)
        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED,
            )
            for future in done:
                endpoint = future_endpoints[future]
                for entry in fetcher.iter_entries(endpoint, future.result()):
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
    return [entry async for entry in fetcher]


def run(coro):
    """Lightweight backport of asyncio.run().
    """
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coro)


def test_basic():
    pypi = SimpleRepository("https://pypi.org/simple")
    entries = run(fetch(pypi, Requirement("pip>=9,<10")))
    assert len(entries) >= 8, entries
