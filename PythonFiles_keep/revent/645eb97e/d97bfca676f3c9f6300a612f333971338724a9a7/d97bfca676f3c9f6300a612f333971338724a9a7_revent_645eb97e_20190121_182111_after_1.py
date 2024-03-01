#!/usr/bin/env python3

from revent import sub, loop

def t(a, b):
    print(a, b)
def t2(c):
    print(c)

def i():
    @sub
    @sub("foo")
    def test(a, b=999, **kw):
        print("test", a, b, kw)


if __name__ == '__main__':
    i()
    loop()
    """
    or at command line:
    python -m revent test
    """
