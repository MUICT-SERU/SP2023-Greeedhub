import unittest

from app import dct_arg


class TestConfigurable(unittest.TestCase):
    def test_fct_generic(self):
        @dct_arg
        def assert_call(*args, e1, e2=2, **kwargs):
            self.assertEqual(0, args[0])
            self.assertEqual(1, e1)
            self.assertEqual(2, e2)
            self.assertEqual(3, kwargs['e3'])

        assert_call({}, 0, e1=1, e2=2, e3=3)
        assert_call({'e1': 1, 'e2': 2, 'e3': 3}, 0, e3=3)
        assert_call({'e1': 1}, 0, e3=3)
        assert_call({'e1': 1, 'e3': 0}, 0, e3=3)

    def test_fct_no_pos(self):
        @dct_arg
        def assert_call(e0, e1=1, *, e2=2, e3):
            self.assertEqual(0, e0)
            self.assertEqual(1, e1)
            self.assertEqual(2, e2)
            self.assertEqual(3, e3)

        assert_call({}, 0, 1, e2=2, e3=3)
        assert_call({}, 0, 1, e3=3)
        assert_call({'e1': 1, 'e0': 0, 'e3': 3})
        assert_call({'e1': 1, 'e0': 2, 'e3': 3}, e0=0)
        self.assertRaises(TypeError, assert_call, {}, 0, e0=0)

    def test_replace_default(self):
        @dct_arg
        def assert_call(e0=3):
            self.assertEqual(0, e0)

        assert_call({}, 0)
        assert_call({}, e0=0)
        assert_call({'e0': 1}, e0=0)
        assert_call({'e0': 0})

    def test_path(self):
        @dct_arg(path='child/subchild')
        def assert_call(e0, e1):
            self.assertEqual(0, e0)
            self.assertEqual(1, e1)

        assert_call({'child': {'subchild': {'e1': 1, 'e0': 0}}})
        assert_call({'child': {'subchild': {'e1': 1}}}, e0=0)
        assert_call(e0=0, e1=1)

    def tests_fetch_conf(self):
        @dct_arg(fetch_args={'config': ""}, name='configuration')
        def assert_call(config, e0):
            self.assertEqual({'e0': 0}, config)
            self.assertEqual(0, e0)

        assert_call(configuration={'e0': 0})

    def test_double_conf(self):
        @dct_arg(name='conf_0')
        @dct_arg(name='conf_1')
        def assert_call(e_0, e_1):
            self.assertEqual(0, e_0)
            self.assertEqual(1, e_1)

        assert_call(conf_1={'e_1': 1}, conf_0={'e_0': 0})
        assert_call(conf_1={'e_1': 1}, e_0=0)
        assert_call(e_1=1, e_0=0)


if __name__ == '__main__':
    unittest.main()
