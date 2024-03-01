from anachronos.test.assertion_fixture import AssertionFixture
from anachronos.test.boot.test_runner import _register


class TestCase(object):

    def __init__(self):
        _register(None, self.__class__)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def assertThat(self, x):
        return AssertionFixture(x)

    def assertEqual(self, expected, actual):
        assert expected == actual

    def assertTrue(self, actual):
        assert bool(actual)

    def assertFalse(self, actual):
        assert not bool(actual)
