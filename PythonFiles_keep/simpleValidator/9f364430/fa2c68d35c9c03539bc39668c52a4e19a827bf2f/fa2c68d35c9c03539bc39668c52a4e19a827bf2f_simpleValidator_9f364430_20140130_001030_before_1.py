# -*- coding: utf-8 -*-

from simplevalidator.rules import *
import unittest


class RulesTest(unittest.TestCase):

    def test_Required_missing_fail(self):
        t = required('')

        self.assertFalse(t)

    def test_Required_fail(self):
        t = required(' ')

        self.assertFalse(t)

    def test_Required_integer_pass(self):
        t = required(1)

        self.assertTrue(t)

    def test_Required_string_pass(self):
        t = required('mystring')

        self.assertTrue(t)

    def test_Min_malformed(self):

        try:
            t = min('', '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Min_string_pass(self):

        t = min('chars', 3)

        self.assertTrue(t)

    def test_Min_string_fail(self):
        t = min('chars', 6)

        self.assertFalse(t)

    def test_Min_integer_fail(self):
        t = min(1, 5)

        self.assertFalse(t)

    def test_Min_integer_pass(self):
        t = min(7, 5)

        self.assertTrue(t)


    def test_Max_malformed(self):

        try:
            t = max('', '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Max_string_fail(self):
        t = max('chars', 3)

        self.assertFalse(t)

    def test_Max_string_pass(self):
        t = max('chars', 6)

        self.assertTrue(t)

    def test_Max_integer_pass(self):
        t = max(1, 5)

        self.assertTrue(t)

    def test_Max_integer_fail(self):
        t = max(7, 5)

        self.assertFalse(t)


    def test_Between_malformed(self):

        try:
            t = between('', '')
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_Between_string_pass(self):
        t = between('chars', '3,6')

        self.assertTrue(t)

    def test_Between_string_fail(self):
        t = between('chars', '7,8')

        self.assertFalse(t)

    def test_Between_integer_pass(self):
        t = between(1, '0,3')

        self.assertTrue(t)

    def test_Between_integer_fail(self):
        t = between(7, '0,3')

        self.assertFalse(t)



    def test_ipv4_malformed(self):
        t = ip4('ah.234.52.12')

        self.assertFalse(t)

    def test_ipv4_wellformed_badvalue_fail(self):
        t = ip4('192.168.299.1')

        self.assertFalse(t)

    def test_ipv4_pass(self):
        t = ip4('192.168.1.55')

        self.assertTrue(t)




    def test_ipv6_malformed(self):
        t = ip6('2001:0:0:0:DB8:800:200C:GIBE')

        self.assertFalse(t)

    def test_ipv6_pass(self):
        t = ip6('2001:0:0:0:DB8:800:200C:417A')

        self.assertTrue(t)




    def test_url_malformed(self):
        t = url('http//google.com')

        self.assertFalse(t)

    def test_url_malformed2(self):
        t = url('https://google')

        self.assertFalse(t)

    def test_url_http_pass(self):
        t = url('http://google.com')

        self.assertTrue(t)

    def test_url_https_pass(self):
        t = url('https://google.com')

        self.assertTrue(t)



    """ 
        Note, as we are trying to do numerical conversions on the fly 
        it is not necessary to do every possible combinations of tests 
    """


    def test_numeric_malformed(self):
        t = numeric('-12334.aaa')

        self.assertFalse(t)

    def test_numeric_pass(self):
        t = numeric('-2324.2454')

        self.assertTrue(t)



    def test_integer_malformed(self):
        t = integer('1234fdd')

        self.assertFalse(t)


    def test_integer_pass(self):
        t = integer('-10')

        self.assertTrue(t)


    def test_posinteger_fail(self):
        t = posinteger(-2)

        self.assertFalse(t)

    def test_posinteger_pass(self):
        t = posinteger('22')

        self.assertTrue(t)



    def test_date_malformed(self):
        t = date('abcedejwwhdnf', '%Y-%m-%d')

        self.assertFalse(t)

    def test_date_fail(self):
        t = date('2014-31-08', '%Y-%m-%d')

        self.assertFalse(t)

    def test_date_pass(self):
        t = date('2014-08-31', '%Y-%m-%d')

        self.assertTrue(t)



    def test_alpha_fail(self):
        t = alpha('abcd1234-93927ss.sorowrj')

        self.assertFalse(t)

    def test_alpa_pass(self):
        t = alpha('abcdefjefohehiwoiwgdbkckouergthoehwppwd')

        self.assertTrue(t)


    def test_alpha_num_fail(self):
        t = alpha_num('ajsgdkgskgdksds-230820840248.453knkdfsds;234552')

        self.assertFalse(t)

    def test_alpha_num_pass(self):
        t = alpha_num('dkhfhieheieheordj38043080383')

        self.assertTrue(t)


    def test_alpha_dash_fail(self):
        t = alpha_dash('sldgshdshd.w293272932.3-4-52ouihcehhdk224;;')

        self.assertFalse(t)


    def test_alpha_dash_pass(self):
        t = alpha_dash('247492742-skdhskhdkshd-2324kjkjksjk_esldd-35lj35j__s--sdskhsdk 232kjk skdl')

        self.assertTrue(t)

if __name__ == '__main__':
    unittest.main()