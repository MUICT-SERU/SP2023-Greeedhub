#!/usr/bin/env python3

from revent import sub, loop

def t(a, b):
    print(a, b)
def t2(c):
    print(c)

@sub
@sub("foo")
def test(a, b, **kw):
    print("test", a, b, kw)


if __name__ == '__main__':
    loop()
    """
    or at command line:
    python -m revent test
    """
