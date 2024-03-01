from simplevalidator import Validator
import unittest

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
    def test_method_extend_fail_pass(self):
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
    def test_method_extend_pass_pass(self):
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


if __name__ == '__main__':
    unittest.main()