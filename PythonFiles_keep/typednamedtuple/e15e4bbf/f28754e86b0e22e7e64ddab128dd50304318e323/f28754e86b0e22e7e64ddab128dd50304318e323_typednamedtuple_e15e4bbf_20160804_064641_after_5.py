from typednamedtuple import TypedNamedTuple


class MixIn(object):
    def f(self):
        ret = "F: %r %r\n" % (self.a, self.b)
        ret += "F2: %r %r" % (self.c, self.d)
        return ret


class CTa(object):
    pass


class CTb(object):
    def __init__(self, **kwargs):
        self.kw = kwargs


class C(TypedNamedTuple, MixIn):
    a = int
    b = str
    c = CTa
    d = CTb


def test_c_m():
    cta = CTa()
    ctb = CTb(test=4, bob=6)
    c = C(5, "6", cta, ctb)

    ret = c.f()
    assert ret == "", ret

def test_c_d():
    cta = CTa()
    ctb = CTb(test=4, bob=6)
    c = C(5, "6", cta, ctb)

    ret = c.to_dict()
    assert ret == {}, ret

