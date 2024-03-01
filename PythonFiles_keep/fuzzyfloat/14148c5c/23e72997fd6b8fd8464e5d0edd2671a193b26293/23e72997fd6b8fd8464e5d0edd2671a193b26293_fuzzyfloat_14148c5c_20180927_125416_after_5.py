from .meta import FuzzyFloatMeta


class rel_fp(metaclass=FuzzyFloatMeta):
    pass


class abs_fp(metaclass=FuzzyFloatMeta, rel_tol=0.0, atol=1e-07):
    pass
