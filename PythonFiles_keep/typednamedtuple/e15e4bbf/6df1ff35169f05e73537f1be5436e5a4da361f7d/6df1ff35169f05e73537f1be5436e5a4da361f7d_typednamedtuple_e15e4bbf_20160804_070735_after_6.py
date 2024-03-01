from __future__ import absolute_import, print_function, unicode_literals

from nose.tools import assert_raises, eq_

from typednamedtuple import TypedNamedTuple


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
    a = int
    b = str
    c = CTa
    d = CTb


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
