#!/usr/bin/env python3

import collections
import json
import os
import traceback

import redis


def init_redis_cli():
    """
    redis.Redis.from_url(None)  # default is localhost:6379
    redis.Redis.from_url("redis://[:password]@redis.host[:6379]/0")
    """
    url = os.environ.get("URL_REDIS", "redis://")
    return redis.Redis.from_url(url)


redis_cli = init_redis_cli()
pubsub = redis_cli.pubsub()
callbacks = collections.defaultdict(set)
ns = "event:"


def emit(key, **kwargs):
    payload = json.dumps(kwargs, ensure_ascii=False)
    return redis_cli.publish(ns + key, payload)


def subscribe(key, func):
    """Supported
    def f1(a, b): pass
    def f1(a, b, **kw): pass
    """
    key = (ns + key).encode()
    callbacks[key].add(func)
    pubsub.subscribe(key)


def sub(key):
    """
    decorator

    @sub("event_foo")
    def do_some_thing(a, b):
        ...

    @sub
    def event_bar(a, b):
        ...

    # but at this version, do not use default value, it has no effect
    @sub
    def event_bar(a, b="x"):
        `b` will set to None if event payload has no `b`,
        so declare default value "x" is redundant
    """

    if hasattr(key, "__code__"):
        func = key
        return sub(func.__name__)(func)

    def wrap(func):
        subscribe(key, func)
        return func
    return wrap


def loop():
    for i in pubsub.listen():
        if i["type"] != "message":
            continue
        try:
            data = json.loads(i["data"].decode())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        for fn in callbacks[i["channel"]]:
            kwargs = data.copy()
            c = fn.__code__
            args = [kwargs.pop(c.co_varnames[i], None)
                    for i in range(c.co_argcount)]
            if len(c.co_varnames) == c.co_argcount:
                kwargs.clear()
            try:
                fn(*args, **kwargs)
            except Exception:
                traceback.print_exc()

# END
