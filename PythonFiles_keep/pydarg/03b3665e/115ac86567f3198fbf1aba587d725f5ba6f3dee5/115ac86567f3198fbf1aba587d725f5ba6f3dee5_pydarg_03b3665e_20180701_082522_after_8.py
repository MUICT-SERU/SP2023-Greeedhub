import unittest

from mapyconf.app import conf_arg


class TestConfigurable(unittest.TestCase):
    def test_fct_generic(self):
        @conf_arg
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
        @conf_arg
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
        @conf_arg
        def assert_call(e0=3):
            self.assertEqual(0, e0)

        assert_call({}, 0)
        assert_call({}, e0=0)
        assert_call({'e0': 1}, e0=0)
        assert_call({'e0': 0})

    def test_path(self):
        @conf_arg(path='child/subchild')
        def assert_call(e0, e1):
            self.assertEqual(0, e0)
            self.assertEqual(1, e1)

        assert_call({'child': {'subchild': {'e1': 1, 'e0': 0}}})
        assert_call({'child': {'subchild': {'e1': 1}}}, e0=0)

    def test_foward_conf_with_name(self):
        @conf_arg(forwardable=True, name='configuration')
        def assert_call(configuration, e0):
            self.assertEqual({'e0': 0}, configuration)
            self.assertEqual(0, e0)

        assert_call(configuration={'e0': 0})

    def test_double_conf(self):
        @conf_arg(name='conf_0')
        @conf_arg(name='conf_1')
        def assert_call(e_0, e_1):
            self.assertEqual(0, e_0)
            self.assertEqual(1, e_1)

        assert_call(conf_1={'e_1': 1}, conf_0={'e_0': 0})
        assert_call(conf_1={'e_1': 1}, e_0=0)
        assert_call(e_1=1, e_0=0)



if __name__ == '__main__':
    unittest.main()
