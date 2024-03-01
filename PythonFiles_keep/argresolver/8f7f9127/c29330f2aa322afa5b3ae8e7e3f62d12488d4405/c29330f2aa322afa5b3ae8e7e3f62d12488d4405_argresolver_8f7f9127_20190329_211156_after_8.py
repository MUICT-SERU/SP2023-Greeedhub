import pytest

from argresolver import ConstResolver, Resolver, MapResolver, ChainResolver, EnvironmentResolver
from argresolver.utils import modified_environ


def test_resolver_wrong_args_passed():
    with pytest.raises(TypeError):
        Resolver(ignore=0)

    with pytest.raises(TypeError):
        Resolver(default_override="nope!")

    with pytest.raises(TypeError):
        MapResolver(mapping=["list"])

    with pytest.raises(TypeError):
        ChainResolver(Resolver(), 'no_resolver!')

    with pytest.raises(TypeError):
        EnvironmentResolver(prefix=0)


def test_environment_resolver_for_unset_var():
    class _Test:
        @EnvironmentResolver()
        def work(self, my_var):
            return my_var

    with modified_environ('MY_VAR'):
        with pytest.raises(TypeError) as err:
            _Test().work()
        assert "work() missing 1 required positional argument: 'my_var'" in str(err)


def test_resolve_in_child():
    class _Base:
        @ConstResolver('base')
        def work(self, a):
            return a

    class _Child(_Base):
        pass

    assert _Base().work() == 'base'
    assert _Child().work() == 'base'


def test_resolve_in_child_with_new_resolver():
    class _Base:
        @ConstResolver('base')
        def work(self, a):
            return a

    class _Child(_Base):
        @ConstResolver('child')
        def work(self, a):
            return a

    assert _Base().work() == 'base'
    assert _Child().work() == 'child'


def test_resolve_in_child_with_init():
    class _Base:
        @ConstResolver('base')
        def __init__(self, a):
            self.a = a

    class _Child(_Base):
        pass

    _base = _Base()
    _child = _Child()

    assert _base.a == 'base'
    assert _child.a == 'base'
