# Test namedtuple like behaviour of typednamedtuple.

# These tests were drawn from:
# https://hg.python.org/cpython/file/5efdef26c821/Lib/test/test_collections.py
# thus, this file is covered by PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# instead of BSD.

from __future__ import absolute_import, print_function, unicode_literals

import copy
import pickle
from collections import OrderedDict
from random import choice 
import string 

import six
if six.PY2:
    import cPickle

from nose.tools import eq_
from nose import SkipTest

from typednamedtuple import TypedNamedTuple, TProp

from tests.test_basic import assert_exception


def test_tupleness():
    class Point(TypedNamedTuple):
        """Point(x, y)"""
        x = TProp(int)
        y = TProp(int)

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
    with assert_exception(IndexError):
        p.__getitem__(3)

    eq_(p.x, x)
    eq_(p.y, y)
    with assert_exception(AttributeError):
        eval('p.z', locals())


def test_factory():
    class Point(TypedNamedTuple):
        """Point(x, y)"""
        x = TProp(int)
        y = TProp(int)

    eq_(Point.__name__, 'Point')
    eq_(Point.__slots__, ())
    eq_(Point.__module__, __name__)
    eq_(Point.__getitem__, tuple.__getitem__)
    eq_(Point._fields, ('x', 'y'))

    # Tests for:
    #  type has non-alpha char
    #  type has keyword
    #  type starts with digit
    #  field with non-alpha char
    #  field has keyword
    #  field starts with digit
    # don't make sense with class based definition of typednamedtuple

    # field with leading underscore is now allowed.
    # Duplicate field now is last copy wins, not an exception anymore.

    # Verify that numbers are allowed in names
    class Point0(TypedNamedTuple):
        x1 = TProp(int)
        y2 = TProp(int)
    eq_(Point0._fields, ("x1", "y2"))

    # Test leading underscores in a typename
    class _(TypedNamedTuple):
        a = TProp(int)
        b = TProp(int)
        c = TProp(int)

    # Previous unicode input tests don't make sense since strings are involved.

    with assert_exception(TypeError):
        Point._make([11])                     # catch too few args
    with assert_exception(TypeError):
        Point._make([11, 22, 33])             # catch too many args


def test_factory_doc_attr():
    class Point(TypedNamedTuple):
        """Point(x, y)"""
        x = TProp(int)
        y = TProp(int)

    eq_(Point.__doc__, 'Point(x, y)')


def test_instance():
    class Point(TypedNamedTuple):
        """Point(x, y)"""
        x = TProp(int)
        y = TProp(int)

    p = Point(11, 22)
    eq_(p, Point(x=11, y=22))
    eq_(p, Point(11, y=22))
    eq_(p, Point(y=22, x=11))
    eq_(p, Point(*(11, 22)))
    eq_(p, Point(**dict(x=11, y=22)))

    with assert_exception(TypeError):
        Point(1)                         # too few args
    with assert_exception(TypeError,
                          args=("__new__() takes 2 positional arguments but 3 were given",)):
        Point(1, 2, 3)                   # too many args
    with assert_exception(TypeError):
        Point(XXX=1, y=2)   # wrong keyword argument
    with assert_exception(TypeError):
        Point(x=1)          # missing keyword argument

    eq_(repr(p), 'Point(x=11, y=22)')
    assert '__weakref__' not in dir(p)
    eq_(p, Point._make([11, 22]))        # test _make classmethod
    eq_(p._fields, ('x', 'y'))           # test _fields attribute
    eq_(p._replace(x=1), (1, 22))        # test _replace method
    eq_(p._asdict(), dict(x=11, y=22))   # test _asdict method

    eq_(vars(p), p._asdict())            # verify that vars() works

    try:
        p._replace(x=1, error=2)
    except ValueError:
        pass
    else:
        assert False, 'Did not detect an incorrect fieldname'


def test_odd_sizes():
    class Zero(TypedNamedTuple):
        pass
    eq_(Zero(), ())
    eq_(Zero._make([]), ())
    eq_(repr(Zero()), 'Zero()')
    eq_(Zero()._asdict(), {})
    eq_(Zero()._fields, ())

    class Dot(TypedNamedTuple):
        d = TProp(int)
    eq_(Dot(1), (1,))
    eq_(Dot._make([1]), (1,))
    eq_(Dot(1).d, 1)
    eq_(repr(Dot(1)), 'Dot(d=1)')
    eq_(Dot(1)._asdict(), {'d':1})
    eq_(Dot(1)._replace(d=999), (999,))
    eq_(Dot(1)._fields, ('d',))

    n = 5000
    names = list(set(''.join([choice(string.ascii_letters)
                              for j in range(10)]) for i in range(n)))
    n = len(names)

    class_start = 'class Big(TypedNamedTuple):\n'
    class_def = class_start + "\n".join(["    %s = TProp(int)" % name 
                                         for name in names])

    test_globals = {
        'TypedNamedTuple': TypedNamedTuple,
        'TProp': TProp
    }
    test_locals = {}
    six.exec_(class_def, test_globals, test_locals)
    Big = test_locals['Big']

    b = Big(*range(n))
    eq_(b, tuple(range(n)))
    eq_(Big._make(range(n)), tuple(range(n)))
    for pos, name in enumerate(names):
        eq_(getattr(b, name), pos)
    _ = repr(b)                        # make sure repr() doesn't blow-up
    d = b._asdict()
    d_expected = dict(zip(names, range(n)))
    eq_(d, d_expected)

    b2 = b._replace(**dict([(names[1], 999),(names[-5], 42)]))
    b2_expected = list(range(n))
    b2_expected[1] = 999
    b2_expected[-5] = 42
    eq_(b2, tuple(b2_expected))
    eq_(b._fields, tuple(names))


class TestTNT(TypedNamedTuple):
    x = TProp(int)
    y = TProp(int)
    z = TProp(int)


def test_pickle():
    p = TestTNT(x=10, y=20, z=30)
    if six.PY2:
        pickles = pickle, cPickle
    else:
        pickles = (pickle,)
    for module in pickles:
        loads = getattr(module, 'loads')
        dumps = getattr(module, 'dumps')
        for protocol in -1, 0, 1, 2:
            q = loads(dumps(p, protocol))
            eq_(p, q)
            eq_(p._fields, q._fields)


def test_copy():
    p = TestTNT(10, 20, 30)
    for copier in copy.copy, copy.deepcopy:
        q = copier(p)
        eq_(p, q)
        eq_(p._fields, q._fields)


