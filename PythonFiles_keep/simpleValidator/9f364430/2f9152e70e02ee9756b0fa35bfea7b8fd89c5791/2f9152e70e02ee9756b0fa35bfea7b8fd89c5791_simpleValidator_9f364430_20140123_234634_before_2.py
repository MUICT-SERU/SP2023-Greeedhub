from rules import *
import unittest


class RulesTest(unittest.TestCase):

    def test_Required(self):
        t = required(value = '')

        assert not t

        t = required(value = ' ')

        assert not t

        t = required(value = 1)

        assert t

        t = required(value = 'mystring')

        assert t

    def test_Min(self):

        try:
            t = min(value = '', constraint = '')
        except ValueError as e:
            assert b'constraint is missing' in e

        t = min(value = 'chars', constraint = 3)

        assert t

        t = min(value = 'chars', constraint = 6)

        assert not t

        t = min(value = 1, constraint = 5)

        assert not t

        t = min(value = 7, constraint = 5)

        assert t

    def test_Max(self):

        try:
            t = max(value = '', constraint = '')
        except ValueError as e:
            assert b'constraint is missing' in e

        t = max(value = 'chars', constraint = 3)

        assert not t

        t = max(value = 'chars', constraint = 6)

        assert t

        t = max(value = 1, constraint = 5)

        assert t

        t = max(value = 7, constraint = 5)

        assert not t

    def test_Between(self):

        try:
            t = between(value = '', constraint = '')
        except ValueError as e:
            assert b'constraints are missing from the validation rule' in e

        t = between(value = 'chars', constraint = '3,6')

        assert t

        t = between(value = 'chars', constraint = '7,8')

        assert not t

        t = between(value = 1, constraint = '0,3')

        assert t

        t = between(value = 7, constraint = '0,3')

        assert not t





if __name__ == '__main__':
    unittest.main()