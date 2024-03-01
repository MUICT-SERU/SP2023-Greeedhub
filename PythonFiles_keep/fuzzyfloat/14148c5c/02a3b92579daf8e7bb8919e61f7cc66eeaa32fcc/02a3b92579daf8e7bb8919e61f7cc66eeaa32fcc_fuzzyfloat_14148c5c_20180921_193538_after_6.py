import unittest

from fuzzyfloat import rel_fp

class FuzzyFloatTestCase(unittest.TestCase):

    def test_cmp_eq(self):
        value = rel_fp(100.5)

        self.assertEqual(value , 100.5)
        self.assertEqual(value, 100.5000001)
        self.assertEqual(value, 100.4999999)

    def test_cmp_le(self):
        value = rel_fp(100)
        self.assertTrue(value <= 500)
        self.assertTrue(value <= 100)
        self.assertTrue(value <= 99.9999999)
        self.assertFalse(value <= 50)

    def test_cmp_ge(self):
        value = rel_fp(100)
        self.assertTrue(value >= 50)
        self.assertTrue(value >= 100)
        self.assertTrue(value >= 99.9999999)
        self.assertFalse(value >= 500)

    def expect_fp(self, value, expected):
        self.assertEqual(type(value), rel_fp)
        self.assertEqual(value, expected)

    def test_add(self):
        value = rel_fp(100)
        self.expect_fp(value + value, 200)
        self.expect_fp(value + 100, 200)
        self.expect_fp(100 + value, 200)

        value += 100
        self.expect_fp(value, 200)

    def test_sub(self):
        value = rel_fp(100)
        self.expect_fp(value - value, 0)
        self.expect_fp(value - 100, 0)
        self.expect_fp(100 - value, 0)

        value -= value
        self.expect_fp(value, 0)
        value -= 100
        self.expect_fp(value, -100)

    def test_mul(self):
        value = rel_fp(100)
        self.expect_fp(value * value, 100 * 100)
        self.expect_fp(value * 100, 100 * 100)
        self.expect_fp(100 * value, 100 * 100)

        value *= 100
        self.expect_fp(value, 100 * 100)

    def test_div(self):
        value = rel_fp(100)
        self.expect_fp(value / value, 1.0)
        self.expect_fp(value / 100, 1.0)
        self.expect_fp(100 / value, 1.0)

        value /= value
        self.expect_fp(value, 1.0)

    def test_floordiv(self):
        value = rel_fp(111)
        self.expect_fp(value // value, 1)
        self.expect_fp(value // 10, 11)
        self.expect_fp(11 // value, 0)

        value //= 10
        self.expect_fp(value, 11)

    def test_exp(self):
        value = rel_fp(3)
        self.expect_fp(value ** value, 3 ** 3)
        self.expect_fp(value ** 3, 3 ** 3)
        self.expect_fp(3 ** value, 3 ** 3)

    def test_divmod(self):
        pass

    def test_mod(self):
        pass

    def test_abs(self):
        value = rel_fp(-100)
        self.expect_fp(abs(value), 100)

    def test_neg(self):
        value = rel_fp(100)
        self.expect_fp(-value, -100)

if __name__ == '__main__':
    unittest.main()
