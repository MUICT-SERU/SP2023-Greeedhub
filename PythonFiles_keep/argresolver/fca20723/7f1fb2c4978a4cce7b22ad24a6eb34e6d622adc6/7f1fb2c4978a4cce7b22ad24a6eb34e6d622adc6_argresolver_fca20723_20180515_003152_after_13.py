from .context import resolver

from resolver import utils

class A:
    def doit(self):
        pass


def test_get_class_that_defined_method():
    a = A()
    assert utils.get_class_that_defined_method(a.doit) is A
