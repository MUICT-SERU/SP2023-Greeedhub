
def eq_with_tolerances(ftype, rel_tol=1e-09, abs_tol=0.0):
    def fp_eq(a, b):
        return ftype.__le__(abs(a-b), max(rel_tol * max(abs(a), abs(b)), abs_tol))
    return fp_eq

class FuzzyFloatMeta(type):

    def __new__(metaclass, name, bases, clsdict, ftype=float, rel_tol=1e-09, atol=0.0):
        bases = (*bases, ftype)
        fp = type.__new__(metaclass, name, bases, clsdict)

        fp.__eq__ = eq_with_tolerances(ftype, rel_tol, atol)

        fp.__le__ = lambda self, other: self < other or self == other
        fp.__ge__ = lambda self, other: self > other or self == other

        fp.__add__ = fp.__iadd__ = fp.__radd__ = lambda self, other: fp(ftype.__add__(self, other))
        fp.__mul__ = fp.__imul__ = fp.__rmul__ = lambda self, other: fp(ftype.__mul__(self, other))

        fp.__sub__ = fp.__isub__ = lambda self, other: fp(ftype.__sub__(self, other))
        fp.__rsub__ = lambda self, other: fp(ftype.__rsub__(self, other))
        fp.__truediv__ = fp.__itruediv__ = lambda self, other: fp(ftype.__truediv__(self, other))
        fp.__rtruediv__ = lambda self, other: fp(ftype.__rtruediv__(self, other))
        fp.__floordiv__ = lambda self, other: fp(ftype.__floordiv__(self, other))
        fp.__rfloordiv__ = lambda self, other: fp(ftype.__rfloordiv__(self, other))
        fp.__mod__ = lambda self, other: fp(ftype.__mod__(self, other))
        fp.__rmod__ = lambda self, other: fp(ftype.__rmod__(self, other))
        fp.__pow__ = lambda self, other: fp(ftype.__pow__(self, other))
        fp.__rpow__ = lambda self, other: fp(ftype.__rpow__(self, other))

        fp.__pos__ = lambda self: fp(ftype.__pos__(self))
        fp.__neg__ = lambda self: fp(ftype.__neg__(self))
        fp.__abs__ = lambda self: fp(ftype.__abs__(self))
        fp.__round__ = lambda self: fp(ftype.__round__(self))

        fp.__divmod__ = lambda self, other: tuple(fp(r) for r in ftype.__divmod__(self, other))
        fp.__rdivmod__ = lambda self, other: tuple(fp(r) for r in ftype.__rdivmod__(self, other))

        fp.__str__ = lambda self: '%s' % ftype.__str__(self)
        fp.__repr__ = lambda self: '%s(%s)' % (name, ftype.__repr__(self))

        return fp


class rel_fp(metaclass=FuzzyFloatMeta):
    pass

class abs_fp(metaclass=FuzzyFloatMeta, rel_tol=0.0, atol=1e-07):
    pass