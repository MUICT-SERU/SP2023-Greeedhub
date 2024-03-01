from __future__ import absolute_import, print_function, unicode_literals

from contextlib import contextmanager

from nose.tools import assert_raises, eq_

from typednamedtuple import (TypedNamedTuple, TProp, IntProp, StrProp,
                             FloatProp)


class MixIn(object):
    def f(self):
        return ("F:", self.a, self.b, self.c, self.d)


class CTa(object):
    def __repr__(self):
        return "CTa()"


class CTb(object):
    def __init__(self, **kwargs):
        self.kw = kwargs

    def __repr__(self):
        return "CTb(%r)" % self.kw


class C(TypedNamedTuple, MixIn):
    a = TProp(int)
    b = TProp(str)
    c = TProp(CTa)
    d = TProp(CTb)


def test_class_mixin():
    cta = CTa()
    ctb = CTb(test=4, bob=6)
    c = C(5, "6", cta, ctb)

    ret = c.f()
    print("R1:", ret)
    eq_(ret[0], "F:")
    eq_(ret[1], 5)
    eq_(ret[2], u'6')
    eq_(repr(ret[3]), repr(CTa()))
    eq_(ret[4].kw, {'bob': 6, 'test': 4})


def test_class_to_dict():
    cta = CTa()
    ctb = CTb(test=4, bob=6)
    c = C(5, "6", cta, ctb)

    eq_(c.a, 5)

    ret = c.to_dict()
    eq_(ret, {'a': 5, 'b': u'6', 'c': cta, 'd': ctb})

    print("cc:", dir(C))
    print("cc:", C.__class__)


def test_class_type_check():
    cta = CTa()
    ctb = CTb(test=4, bob=6)

    print(dir(C))
    print("C_f:", C._fields)
    print("C_t:", C._types)

    with assert_raises(TypeError):
        C._type_check({}, "54", cta, ctb)


def test_class_type_err():
    cta = CTa()
    ctb = CTb(test=4, bob=6)

    print(dir(C))
    print("C_f:", C._fields)
    print("C_t:", C._types)

    with assert_raises(TypeError):
        c = C({}, "5", cta, ctb)


def test_class_keyword_arg():
    class Pt(TypedNamedTuple):
        x = TProp(int)
        y = TProp(int)

    p = Pt(y=6, x=10)
    eq_(p, (10, 6))


def test_class_mixed_arg():
    class Pt(TypedNamedTuple):
        x = TProp(int)
        y = TProp(int)

    p = Pt(6, y=10)
    eq_(p, (6, 10))


def test_class_check_kw_pos_eq():
    # Check that instances made with keyword args and with 
    # positional args are the same
    class Pt(TypedNamedTuple):
        y = TProp(int)
        x = TProp(int)

    p = Pt(10, 6)

    p2 = Pt(y=10, x=6)
    eq_(p, p2)
    eq_(str(p), str(p2))
    eq_(repr(p), repr(p2))


@contextmanager
def assert_exception(cls, eval_exc=None, args=None):
    fired = False
    caught_exc = None
    try:
        yield
    except cls as exc:
        fired = True
        caught_exc = exc

    if caught_exc and eval_exc is not None:
        assert eval_exc(caught_exc)
    if caught_exc and args is not None:
        assert caught_exc.args == args, args
    if not fired:
        assert False, "Exception (%s) failed to fire." % cls.__name__


def test_class_missing_position():
    class Pt(TypedNamedTuple):
        x = TProp(int)
        y = TProp(int)

    with assert_exception(TypeError,
                          args=("Pt missing 1 required positional argument: 'y'",)):
        p = Pt(6)

def test_class_missing_mixed():
    class Pt(TypedNamedTuple):
        x = TProp(int)
        y = TProp(int)

    exc_arg = ("Pt missing 1 required positional argument: 'x'",)
    with assert_exception(TypeError,
                          eval_exc=lambda exc: exc.args == exc_arg):
        p = Pt(y=6)


def test_class_missing_kw():
    class Pt(TypedNamedTuple):
        x = TProp(int)
        y = TProp(int)

    with assert_exception(TypeError,
                          args=("Pt missing 1 required positional argument: 'y'",)):
        p = Pt(x=6)


def test_partials():
    class Pt(TypedNamedTuple):
        x = IntProp()
        y = FloatProp()
        z = StrProp()

    p = Pt(1, 2.0, "3.0")
    eq_(p, (1, 2.0, "3.0"))


def test_strict_int():
    class StrictInt(int):
        def __init__(self, i):
            assert type(i) is int
            super(StrictInt, self).__init__()
            self = i


    class Pt(TypedNamedTuple):
        x = TProp(StrictInt)

    p = Pt(1)
    eq_(p, (1,))

    with assert_raises(AssertionError):
        p = Pt("1")


if __name__=="__main__":

    print("Running test_class_type_check()...",)
    test_class_type_check()
    print("passed")

    print("Running test_class_type_err()...",)
    test_class_type_err()
    print("passed")

    print("Running test_class_mixin()...",)
    test_class_mixin()
    print("passed")

    print("Running test_class_d()...",)
    test_class_to_dict()
    print("passed")
