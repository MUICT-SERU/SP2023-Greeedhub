import unittest

from mapyconf.App import configurable


class TestConfigurable(unittest.TestCase):

    def test_fct_generic(self):
        @configurable
        def assert_call(*args, e1, e2=2, **kwargs):
            self.assertEquals(0, args[0])
            self.assertEquals(1, e1)
            self.assertEquals(2, e2)
            self.assertEquals(3, kwargs['e3'])

        assert_call({}, 0, e1=1, e2=2, e3=3)
        assert_call({'e1': 1, 'e2': 2, 'e3': 3}, 0, e3=3)
        assert_call({'e1': 1}, 0, e3=3)
        assert_call({'e1': 1, 'e3': 0}, 0, e3=3)

    def test_fct_no_pos(self):
        @configurable
        def assert_call(e0, e1=1, *, e2=2, e3):
            self.assertEquals(0, e0)
            self.assertEquals(1, e1)
            self.assertEquals(2, e2)
            self.assertEquals(3, e3)

        assert_call({}, 0, 1, e2=2, e3=3)
        assert_call({}, 0, 1, e3=3)
        assert_call({'e1': 1, 'e0': 0, 'e3': 3})
        assert_call({'e1': 1, 'e0': 2, 'e3': 3}, e0=0)
        self.assertRaises(TypeError, assert_call, {}, 0, e0=0)

    def test_replace_default(self):
        @configurable
        def assert_call(e0=3):
            self.assertEquals(0, e0)

        assert_call({}, 0)
        assert_call({}, e0=0)
        assert_call({'e0': 1}, e0=0)
        assert_call({'e0': 0})

    def test_path(self):
        @configurable(path='child/subchild')
        def assert_call(e0, e1):
            self.assertEquals(0, e0)
            self.assertEquals(1, e1)

        assert_call({'child': {'subchild': {'e1': 1, 'e0': 0}}})
        assert_call({'child': {'subchild': {'e1': 1}}}, e0=0)

    def test_foward_conf_with_name(self):
        @configurable(forward_conf=True, conf_arg='configuration')
        def assert_call(configuration, e0):
            self.assertEquals({'e0': 0}, configuration)
            self.assertEquals(0, e0)

        assert_call(configuration={'e0': 0})


if __name__ == '__main__':
    unittest.main()
