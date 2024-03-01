# Test namedtuple like behaviour of typednamedtuple.

# These tests were drawn from:
# https://hg.python.org/cpython/file/5efdef26c821/Lib/test/test_collections.py
# thus, this file is covered by PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# instead of BSD.

from __future__ import absolute_import, print_function, unicode_literals

import six

import pickle
if six.PY2:
    import cPickle

from nose.tools import assert_raises, eq_
from nose import SkipTest

from typednamedtuple import TypedNamedTuple

class Point(TypedNamedTuple):
    x = int
    y = int


def test_tupleness():
    p = Point(11, 22)
    
    assert isinstance(p, tuple)
    eq_(p, (11, 22))            # matches a real tuple
    eq_(tuple(p), (11, 22))     # coercable to a real tuple
    eq_(list(p), [11, 22])      # coercable to a list
    eq_(max(p), 22)             # iterable
    eq_(max(*p), 22)            # star-able
    x, y = p
    eq_(p, (x, y))              # unpacks like a tuple
    eq_((p[0], p[1]), (11, 22)) # indexable like a tuple
    with assert_raises(IndexError):
        p.__getitem__(3)

    eq_(p.x, x)
    eq_(p.y, y)
    with assert_raises(AttributeError):
        eval('p.z', locals())


