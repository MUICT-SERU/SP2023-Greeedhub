# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from simplevalidator import Validator, i18n
from simplevalidator.rules import *
import unittest

### validator class inner method unittest
class ClassTest(unittest.TestCase):
    
    def setUp(self):
        pass


    def test_malformed_field_argument_constructor(self):
        wrongfields = ''
        rules = {'myField': 'required'}

        try :
            v = Validator(fields = wrongfields, rules = rules)
        except TypeError as e:
            self.assertRaisesRegexp(e, 'field data must be a dict')

    def test_malformed_rules_argument_constructor(self):
        fields = {'myField': 'some data'}
        wrongrules = None

        try :
            v = Validator(fields = fields, rules = wrongrules)
        except TypeError as e:
            self.assertRaisesRegexp(e, 'rules data must be a dict')

    def test_malformed_messages_argument_constructor(self):
        fields = {'myField': 'some data'}
        rules = {'myField': 'required'}
        wrongmessages = ''

        try :
            v = Validator(fields = fields, rules = rules, messages = wrongmessages)
        except TypeError as e:
            self.assertRaisesRegexp(e, 'custom error messages must be contained in a dict')

    def test_wellformed_field_no_corresponding_rule(self):
        fields = {'myField': 'some data'}
        rules = {'myField2': 'required'}

        try :
            v = Validator(fields = fields, rules = rules)
        except ValueError as e:
            self.assertRaisesRegexp(e, 'fields do not correspond to rules')

    def test_wellformed_field_no_corresponding_message(self):
        fields = {'myField': 'some data'}
        rules = {'myField': 'required'}
        messages = {'requiredd': '{} is not required'}

        try :
            v = Validator(fields = fields, rules = rules, messages = messages)
        except ValueError as e:
            self.assertRaisesRegexp(e, 'custom validation messages do not correspond to rule list')

    
    """
        Notice: in these two methods we "override" an existant rule message !
        Because of this, the message will be changed through the life of the APP
        IF the validation is global and not loaded in a context (somewhere it really should, for example)
    """
    def test_wellformed_all_validation_fail(self):

        fields = {'myField': ''}
        rules = {'myField': 'required'}

        """ Error message is the opposite of the "rule" on purpose """
        messages = {'required': '{} is never required'}

        v = Validator(fields = fields, rules = rules, messages = messages)

        self.assertTrue(v.fails())
        self.assertTrue('myField is never required' in v.errors())

    def test_wellformed_all_validation_pass(self):

        fields = {'myField': 'itsa me, mario !'}
        rules = {'myField': 'required'}

        """ Error message is the opposite of the "rule" on purpose """
        messages = {'required': '{} is never required'}

        v = Validator(fields = fields, rules = rules, messages = messages)

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())

    """
        Because of the merging of all tests in just one file, the original message must be reset :) !
        That's why the filler method below was added
        


    """

    def test_wellformed_all_validation_pass_message_reset_pass(self):

        fields = {'myField': 'itsa me, mario !'}
        rules = {'myField': 'required'}

        messages = {'required': '{} is required'}

        v = Validator(fields = fields, rules = rules, messages = messages)

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())

    def test_malformed_dict_extend(self):

        new_rule = 'somegibberish'
        v = Validator()
        
        try:
            v.extend(new_rule)
        except TypeError as e:
            self.assertRaisesRegexp(e, 'custom rule must be a dict')


    def test_malformed_method_extend(self):

        self.falsemethod = ''

        new_rule = {'new_rule': self.falsemethod}

        v = Validator()

        try:
            v.extend(new_rule)
        except TypeError as e:
            self.assertRaisesRegexp(e, 'custom rule is not a callable')


    """
        I mean here that the validation fails, thus the method is called
    """
    def test_extend_fail_pass(self):
        messages = {'new_rule': '{} is less than 10 !!'}
        new_rule = {'new_rule': self.good_method}
        fields = {'cars': 5}
        rules = {'cars': 'new_rule'}

        v = Validator()
        v.extend(new_rule)

        v.make(fields = fields, rules = rules, messages = messages)

        self.assertTrue(v.fails())
        self.assertTrue('cars is less than 10 !!' in v.errors())

    """
        Same test, but this time the validation passes totally
    """
    def test_extend_pass_pass(self):
        messages = {'new_rule': '{} is less than 10 !!'}
        new_rule = {'new_rule': self.good_method}
        fields = {'cars': 12}
        rules = {'cars': 'new_rule'}

        v = Validator()
        v.extend(new_rule)

        v.make(fields = fields, rules = rules, messages = messages)

        self.assertFalse(v.fails())
        self.assertFalse(v.errors())



    def good_method(self, value):
        return value > 10

### Validations behavior unit tests
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


### Rules unit tests
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