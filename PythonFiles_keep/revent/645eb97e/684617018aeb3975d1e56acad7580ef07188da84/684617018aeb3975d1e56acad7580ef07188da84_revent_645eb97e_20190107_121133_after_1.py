#!/usr/bin/env python3

import importlib
import sys

from . import sub, loop


def main():
    modules = sys.argv[1:]
    if not modules:
        return print("usage:\npython -m revent mod_1 [, mod_2, mod_3, ...]")
    for module_name in sys.argv[1:]:
        module = importlib.import_module(module_name)
        for name in dir(module):
            if name.startswith("_"):
                continue
            fn = getattr(module, name)
            if hasattr(fn, "__code__") and fn.__module__ == module_name:
                sub(fn)
    # run forever
    loop()


if __name__ == '__main__':
    main()
