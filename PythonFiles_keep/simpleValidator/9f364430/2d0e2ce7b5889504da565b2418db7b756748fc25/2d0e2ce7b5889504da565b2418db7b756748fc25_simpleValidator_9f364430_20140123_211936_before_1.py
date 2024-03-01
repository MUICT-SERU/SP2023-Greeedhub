from validator import Validator
import unittest


class ValidatorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_validationRequired(self):
        v = Validator({'test': ''}, {'test': 'required'})

        assert v.fails() == True
        assert b'test is required' in v.errors()

        v = Validator({'test': 'myvalue'}, {'test': 'required'})

        assert v.fails() == False
        assert not v.errors()

    def test_validationEmail(self):
        v = Validator({'test': 'fake.email.com'}, {'test': 'email'})

        assert v.fails() == True
        assert b'test is not a valid email' in v.errors()

        v = Validator({'test': 'fake@email.com'}, {'test': 'email'})

        assert v.fails() == False
        assert not v.errors()

    def test_validationMin(self):
        try:
            v = Validator({'test': '5char'}, {'test': 'min'})
        except ValueError as e:
            assert b'constraint is missing' in e

        v = Validator({'test': '5char'}, {'test': 'min:6'})

        assert v.fails() == True
        assert b'test must be more than 6 characters' in v.errors()

        v = Validator({'test': 5}, {'test': 'min:6'})

        assert v.fails() == True
        assert b'test must be higher than 6' in v.errors()

        v = Validator({'test': '7'}, {'test': 'min:6'})

        assert v.fails() == False
        assert not v.errors()


    def test_validationMax(self):
        try:
            v = Validator({'test': '5char'}, {'test': 'max'})
        except ValueError as e:
            assert b'constraint is missing' in e

        v = Validator({'test': '7charss'}, {'test': 'max:6'})

        assert v.fails() == True
        assert b'test must be less than 6 characters' in v.errors()

        v = Validator({'test': 5}, {'test': 'max:4'})

        assert v.fails() == True
        assert b'test must be lower than 4' in v.errors()

        v = Validator({'test': '7'}, {'test': 'max:8'})

        assert v.fails() == False
        assert not v.errors()

    def test_validationBetween(self):
        try:
            v = Validator({'test': '5char'}, {'test': 'between'})
        except ValueError as e:
            assert b'constraints are missing from the validation rule' in e

        v = Validator({'test': '7charss'}, {'test': 'between:8,10'})

        assert v.fails() == True
        assert b'test\'s length must be between 8 and 10 characters' in v.errors()

        v = Validator({'test': 5}, {'test': 'between:8,10'})

        assert v.fails() == True
        assert b'test\'s value must be higher than 8 and lower than 10' in v.errors()

        v = Validator({'test': '9'}, {'test': 'between:8,10'})

        assert v.fails() == False
        assert not v.errors()

    def test_validationMultiple(self):
        v = Validator({'test': ''}, {'test': 'required|email'})

        assert v.fails() == True
        assert b'test is required' in v.errors()
        assert b'test is not a valid email' in v.errors()

        v = Validator({'test': 'myvalue'}, {'test': 'required|email'})

        assert v.fails() == True
        assert b'test is required' not in v.errors()
        assert b'test is not a valid email' in v.errors()

        v = Validator({'test': 'fake@email.com'}, {'test': 'required|email'})

        assert v.fails() == False
        assert not v.errors()

    def test_validationMultiple2(self):
        v = Validator()

        to_test = {
            'name': 'Ken',
            'email': 'ken.fake-email.com',
        }

        rules = {
            'name': 'required',
            'email': 'required|email',
        }

        v.make(to_test, rules)

        assert v.fails() == True
        assert b'email is not a valid email' in v.errors()

        to_test = {
            'name': 'Ken',
            'email': 'ken@fake-email.com',
        }

        rules = {
            'name': 'required',
            'email': 'required|email',
        }

        v.make(to_test, rules)

        assert v.fails() == False
        assert not v.errors()


    def test_customValidation(self):
        v = Validator()
        v.extend({'myrule': self.customRule})

        v.make({'test': 5}, {'test': 'myrule'}, {'myruled' : '{0} is not equal to 1'})

        assert v.fails() == True
        assert b'test is not equal to 1' in v.errors()


    def customRule(self, **kwargs):
        return kwargs['value'] == 1
        


if __name__ == '__main__':
    unittest.main()