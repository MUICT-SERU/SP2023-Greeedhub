#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import os

import aiohttp

from packaging_repositories import Fetcher, SimpleRepository, VersionFilter


def as_future(value):
    future = asyncio.get_event_loop().create_future()
    future.set_result(value)
    return future


async def read_remote_text(session, url):
    response = await session.get(url)
    response.raise_for_status()
    return (await response.read(), response.get_encoding())


async def iter_futures(session, fetcher):
    for endpoint in fetcher.iter_endpoints():
        if endpoint.local:
            path = endpoint.value
            if os.path.isdir(path):
                names = [os.path.join(path, n) for n in os.listdir(path)]
                yield endpoint, as_future(names)
            else:
                with open(path, "rb") as f:
                    yield endpoint, as_future((f.read(), None))
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


async def fetch(repository, requirement, filters):
    fetcher = AIOHTTPFetcher(repository, requirement)
    generator = fetcher
    for f in filters:
        generator = f(generator)
    return [entry async for entry in generator]


def run(coro):
    """Lightweight backport of asyncio.run().
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def test_basic():
    pypi = SimpleRepository("https://pypi.org/simple")
    version_filter = VersionFilter(">=9,<10")
    entries = run(fetch(pypi, "pip", [version_filter]))
    assert len(entries) >= 8, entries
