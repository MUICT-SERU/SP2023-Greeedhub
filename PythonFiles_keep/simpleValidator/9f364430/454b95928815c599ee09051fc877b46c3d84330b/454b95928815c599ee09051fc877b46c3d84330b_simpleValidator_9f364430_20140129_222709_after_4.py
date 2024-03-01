# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from simplevalidator import Validator, i18n
import unittest


class ValidatorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_required_empty(self):
        v = Validator(fields = {'test': ''}, rules = {'test': 'required'})

        self.assertTrue(v.fails())
        self.assertTrue('test is required' in v.errors())

    def test_required_pass(self):
        v = Validator(fields = {'test': 'myvalue'}, rules = {'test': 'required'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())



    def test_email_malformed(self):
        v = Validator(fields = {'test': 'fake.email.com'}, rules = {'test': 'email'})

        self.assertTrue(v.fails())
        self.assertTrue('test must be a valid email' in v.errors())

    def test_email_pass(self):
        v = Validator(fields = {'test': 'fake@email.com'}, rules = {'test': 'email'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())



    def test_min_malformed(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'min'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_min_malformed_non_integer(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'min:omagad'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraint is not a valid integer')
     
    def test_min_string_fail(self):
        v = Validator(fields = {'test': '5char'}, rules = {'test': 'min:6'})

        self.assertTrue(v.fails())
        self.assertTrue('test must be more than 6 characters' in v.errors())
    
    def test_min_integer_fail(self):
        v = Validator(fields = {'test': 5}, rules = {'test': 'min:6'})

        self.assertTrue(v.fails())
        self.assertTrue('test must be higher than 6' in v.errors())

    def test_min_string_integer_pass(self):
        v = Validator(fields = {'test': '7'}, rules = {'test': 'min:6'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())



    def test_max_malformed(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'max'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_max_malformed_non_integer(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'max:omagad'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraint is not a valid integer')
        
    def test_max_string_fail(self):
        v = Validator(fields = {'test': '7charss'}, rules = {'test': 'max:6'})

        self.assertTrue(v.fails())
        self.assertTrue('test must be less than 6 characters' in v.errors())

    def test_max_integer_fail(self):
        v = Validator(fields = {'test': 5}, rules = {'test': 'max:4'})

        self.assertTrue(v.fails())
        self.assertTrue('test must be lower than 4' in v.errors())

    def test_max_string_integer_pass(self):
        v = Validator(fields = {'test': '7'}, rules = {'test': 'max:8'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())





    def test_between_malformed(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'between'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraints are missing from the validation rule')

    def test_between_malformed_non_integer(self):
        v = Validator()

        try:
            v.make(fields = {'test': '5char'}, rules = {'test': 'between:omagad,omagaaaad'})
        except ValueError as e:
            self.assertRaisesRegexp(e, 'constraint is not a valid integer')
        
    def test_between_string_fail(self):
        v = Validator(fields = {'test': '7charss'}, rules = {'test': 'between:8,10'})

        self.assertTrue(v.fails())
        self.assertTrue('test\'s length must be between 8 and 10 characters' in v.errors())

    def test_between_integer_fail(self):
        v = Validator(fields = {'test': 5}, rules = {'test': 'between:8,10'})

        self.assertTrue(v.fails())
        self.assertTrue('test\'s value must be higher than 8 and lower than 10' in v.errors())

    def test_between_string_integer_pass(self):
        v = Validator(fields = {'test': '9'}, rules = {'test': 'between:8,10'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())




    def test_multiple_rule_fail1(self):
        v = Validator(fields = {'test': ''}, rules = {'test': 'required|email'})

        self.assertTrue(v.fails())
        self.assertTrue('test is required' in v.errors())
        self.assertTrue('test must be a valid email' in v.errors())

    def test_multiple_rule_fail2(self):
        v = Validator(fields = {'test': 'myvalue'}, rules = {'test': 'required|email'})

        self.assertTrue(v.fails())
        self.assertTrue('test is required' not in v.errors())
        self.assertTrue('test must be a valid email' in v.errors())

    def test_multiple_rule_pass(self):
        v = Validator(fields = {'test': 'fake@email.com'}, rules = {'test': 'required|email'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())





    def test_multile_fields_rule_fail(self):
        v = Validator()

        to_test = {
            'name': 'Ken',
            'email': 'ken.fake-email.com',
        }

        rules = {
            'name': 'required',
            'email': 'required|email',
        }

        v.make(fields = to_test, rules = rules)

        self.assertTrue(v.fails())
        self.assertTrue('email must be a valid email' in v.errors())



    def test_multile_fields_rule_pass(self):
        v = Validator()

        to_test = {
            'name': 'Ken',
            'email': 'ken@fake-email.com',
        }

        rules = {
            'name': 'required',
            'email': 'required|email',
        }

        v.make(fields = to_test, rules = rules)

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())




    def test_custom_rule_fail(self):
        v = Validator()
        v.extend({'myrule': self.customRule})

        v.make(fields = {'test': 5}, rules = {'test': 'myrule'}, messages = {'myrule' : '{0} is not equal to 1'})

        self.assertTrue(v.fails())
        self.assertTrue('test is not equal to 1' in v.errors())


    def customRule(self, value):
        return value == 1





    def test_date_rule_fail(self):
        v = Validator(fields = {'test': '2451-df-1234'}, rules = {'test': 'date:%Y-%m-%d'})

        self.assertTrue(v.fails())
        self.assertTrue('test is not a valid date, the format must be %Y-%m-%d' in v.errors())

    def test_date_rule_pass(self):
        v = Validator(fields = {'test': '2451-09-12'}, rules = {'test': 'date:%Y-%m-%d'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())


    
    def test_integer_as_string_fail(self):
        v = Validator(fields = {'test': '-10a'}, rules = {'test': 'integer'})

        self.assertTrue(v.fails())
        self.assertTrue("test must be an integer" in v.errors())

    def test_integer_as_string_pass(self):
        v = Validator(fields = {'test': '-10'}, rules = {'test': 'integer'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())


    def test_integer_as_integer_pass(self):
        v = Validator(fields = {'test': 25}, rules = {'test': 'integer'})

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())

    
    def test_email_locale_fr_fail(self):
        
        i18n.switch_language('fr')

        v = Validator(fields = {'test': 'bademail.com'}, rules = {'test': 'email'})

        self.assertTrue(v.fails())

        self.assertTrue('test doit être un email valide' in v.errors())

        ### Switching back locale to English to avoid that other tests fail ! ###
        i18n.switch_language('en')

    
    def test_email_locale_jp_fail(self):
        
        i18n.switch_language('ja')

        v = Validator(fields = {'test': 'bademail.com'}, rules = {'test': 'email'})

        self.assertTrue(v.fails())

        self.assertTrue('testに正しい形式をご指定ください。' in v.errors())

        ### Switching back locale to English to avoid that other tests fail ! ###
        i18n.switch_language('en')


if __name__ == '__main__':
    unittest.main()