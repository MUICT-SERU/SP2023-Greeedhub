from anachronos.test.assertion import Assertion
from anachronos.test.assertion_fixture import AssertionFixture


def _assertion(x):
    def wrapped(*args):
        result = x(*args)
        AssertionFixture._instances.append(result)
        return result

    return wrapped


class AssertionRegistry(object):
    def __init__(self):
        self.assertions = []

    def _register(self, x):
        def wrapped(*args):
            result = x(*args)
            self.assertions.append(result)
            return result

        return wrapped

    def create_fixture(self):
        class RegisteringAssertionFixture(AssertionFixture):
            @self._register
            def is_stored(self) -> Assertion:
                return super().is_stored()
        return RegisteringAssertionFixture
