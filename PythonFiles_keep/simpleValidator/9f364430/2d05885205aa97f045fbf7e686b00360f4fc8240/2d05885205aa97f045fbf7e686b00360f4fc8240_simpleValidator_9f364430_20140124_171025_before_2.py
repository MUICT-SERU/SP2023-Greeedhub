from rules import *
import unittest


class RulesTest(unittest.TestCase):

    def test_Required_missing_fail(self):
        t = required(value = '')

        self.assertFalse(t)

    def test_Required_fail(self):
        t = required(value = ' ')

        self.assertFalse(t)

    def test_Required_integer_pass(self):
        t = required(value = 1)

        self.assertTrue(t)

    def test_Required_string_pass(self):
        t = required(value = 'mystring')

        self.assertTrue(t)

    def test_Min_malformed(self):

        try:
            t = min(value = '', constraint = '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Min_string_pass(self):

        t = min(value = 'chars', constraint = 3)

        self.assertTrue(t)

    def test_Min_string_fail(self):
        t = min(value = 'chars', constraint = 6)

        self.assertFalse(t)

    def test_Min_integer_fail(self):
        t = min(value = 1, constraint = 5)

        self.assertFalse(t)

    def test_Min_integer_pass(self):
        t = min(value = 7, constraint = 5)

        self.assertTrue(t)


    def test_Max_malformed(self):

        try:
            t = max(value = '', constraint = '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Max_string_fail(self):
        t = max(value = 'chars', constraint = 3)

        self.assertFalse(t)

    def test_Max_string_pass(self):
        t = max(value = 'chars', constraint = 6)

        self.assertTrue(t)

    def test_Max_integer_pass(self):
        t = max(value = 1, constraint = 5)

        self.assertTrue(t)

    def test_Max_integer_fail(self):
        t = max(value = 7, constraint = 5)

        self.assertFalse(t)


    def test_Between_malformed(self):

        try:
            t = between(value = '', constraint = '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Between_string_pass(self):
        t = between(value = 'chars', constraint = '3,6')

        self.assertTrue(t)

    def test_Between_string_fail(self):
        t = between(value = 'chars', constraint = '7,8')

        self.assertFalse(t)

    def test_Between_integer_pass(self):
        t = between(value = 1, constraint = '0,3')

        self.assertTrue(t)

    def test_Between_integer_fail(self):
        t = between(value = 7, constraint = '0,3')

        self.assertFalse(t)




if __name__ == '__main__':
    unittest.main()