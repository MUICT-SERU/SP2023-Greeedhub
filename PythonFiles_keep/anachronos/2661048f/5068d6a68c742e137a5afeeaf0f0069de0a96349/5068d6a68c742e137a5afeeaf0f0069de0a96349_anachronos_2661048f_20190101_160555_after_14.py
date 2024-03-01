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
        def wrapped(*args, **kwargs):
            result = x(*args, **kwargs)
            self.assertions.append(result)
            return result

        return wrapped

    def create_fixture(self):
        class RegisteringAssertionFixture(object):
            def __init__(that, x):
                that.fixture = AssertionFixture(x)

            def __getattr__(that, item):
                return self._register(that.fixture.__getattribute__(item))

        return RegisteringAssertionFixture

    def monkey_patch_test_fixture(self, test_fixture) -> None:
        test_fixture.assertThat = lambda x: self.create_fixture()(x)
