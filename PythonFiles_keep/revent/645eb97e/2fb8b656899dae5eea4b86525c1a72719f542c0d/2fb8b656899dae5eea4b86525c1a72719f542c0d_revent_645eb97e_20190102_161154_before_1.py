#!/usr/bin/env python3

import collections
import json
import os
import sys
import traceback

import redis


def init_redis_cli():
    cfg = {"decode_responses": True}
    try:
        with open(os.environ.get("REDIS_YAML", "etc/redis.yaml")) as f:
            import yaml
            cfg.update(yaml.load(f))
    except FileNotFoundError:
        pass
    return redis.Redis(**cfg)


redis_cli = init_redis_cli()
pubsub = redis_cli.pubsub()
callbacks = collections.defaultdict(set)
ns = "event:"


def emit(key, **kw):
    data = json.dumps(kw, default=str, ensure_ascii=False)
    return redis_cli.publish(ns + key, data)


def subscribe(key, func):
    """Supported
    def f1(a, b): pass
    def f1(a, b, **kw): pass
    """
    key = ns + key
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
            data = json.loads(i["data"])
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
