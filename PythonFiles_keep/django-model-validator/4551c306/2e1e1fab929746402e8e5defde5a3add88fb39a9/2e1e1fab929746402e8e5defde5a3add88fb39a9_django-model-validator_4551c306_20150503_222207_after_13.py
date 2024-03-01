from model_validator.mixins import ModelValidationMixin
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from model_mommy import mommy


class TestValidate(TestCase):
    """
    Tests the ModelValidationMixin.validate method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()

    def test_clean_invalid_data(self):
        # clean=True
        # data is invalid
        data = {
            'id': 1,
            'username': 1,     # invalid!
            'last_name': 'Marsh',
        }
        model_class = User
        allowed_fields = ['username', 'last_name']
        clean = True
        
        self.assertRaises(
            ValidationError,
            self.mixin.validate,
            data, model_class, allowed_fields, clean, exclude=None,
        )

    def test_not_clean(self):
        # clean=False
        # data is invalid (but should go through nonetheless) and the model
        # should return
        data = {
            'id': 1,
            'username': 1,     # invalid!
            'last_name': 'Marsh',
        }
        model_class = User
        allowed_fields = ['username', 'last_name']
        clean = False
        
        user = self.mixin.validate(data, model_class, allowed_fields, clean,
                                   exclude=None)

        # assert that ``user`` is an instance of the User model
        self.assertTrue(isinstance(user, User))
        # assert ``user`` field values
        self.assertEqual(user.id, None)
        self.assertEqual(user.username, 1)
        self.assertEqual(user.last_name, 'Marsh')


class TestModelize(TestCase):
    """
    Tests the ModelValidationMixin._modelize method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()

    def test_dict(self):
        data = {
                'id': 1,
                'first_name': 'Randy',
                'last_name': 'Marsh',
                'username': 'randy',
                'email': 'randy@example.com'
        }

        user = self.mixin._modelize(
            data, User, allowed_fields=['first_name', 'last_name']
        )                

        # assert that ``user`` is an instance of the User model
        self.assertTrue(isinstance(user, User))

        # assert the values of the model fields
        self.assertEqual(user.id, None)
        self.assertEqual(user.first_name, 'Randy')
        self.assertEqual(user.last_name, 'Marsh')
        self.assertEqual(user.username, '')
        self.assertEqual(user.email, '')

    def test_list(self):
        data = [
            {
                'id': 1,
                'first_name': 'Randy',
                'last_name': 'Marsh',
                'username': 'randy',
                'email': 'randy@example.com'
            },
            {
                'id': 2,
                'first_name': 'Eric',
                'username': 'cartman',
            },
        ]

        users = self.mixin._modelize(
            data, 
            User, 
            allowed_fields=['first_name', 'last_name']
        )

        # Assert that ``users`` are instances of User model
        self.assertTrue(isinstance(users[0], User))
        self.assertTrue(isinstance(users[1], User))

        # Assert model fields
        self.assertEqual(users[0].id, None)
        self.assertEqual(users[0].first_name, 'Randy')
        self.assertEqual(users[0].last_name, 'Marsh')
        self.assertEqual(users[0].username, '')
        self.assertEqual(users[0].email, '')
        self.assertEqual(users[1].id, None)
        self.assertEqual(users[1].first_name, 'Eric')
        self.assertEqual(users[1].last_name, '')
        self.assertEqual(users[1].username, '')
        self.assertEqual(users[1].email, '')


class TestModelizeDict(TestCase):
    """
    Tests the ModelValidationMixin._modelize_dict method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()
        self.data = {
            'id': 1,
            'first_name': 'Randy',
            'last_name': 'Marsh',
            'username': 'randy',
            'email': 'randy@example.com'
        }

    def test_empty_allowed_fields(self):
        user = self.mixin._modelize_dict(self.data, User, allowed_fields=[])

        # Assert that ``user`` is instance of User model
        self.assertTrue(isinstance(user, User))

        # Assert that for all fields in ``self.data`` the ``user`` model has no value
        self.assertEqual(user.id, None)
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.username, '')
        self.assertEqual(user.email, '')

    def test_non_empty_allowed_fields(self):
        user = self.mixin._modelize_dict(
                   self.data, 
                   User,
                   allowed_fields=['last_name', 'username', 'email']
            )

        # Assert that ``user`` is instance of User model
        self.assertTrue(isinstance(user, User))

        # Assert that ``user.id`` and ``user.first_name`` have no value
        self.assertEqual(user.id, None)
        self.assertEqual(user.first_name, '')
        # Assert that all other 3 field have the correct value
        for field in ('last_name', 'username', 'email'):
            self.assertEqual(getattr(user, field), self.data[field])


class TestModelizeList(TestCase):
    """
    Tests the ModelValidationMixin._modelize_list method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()
        self.data = [
            {   
                'id': 1,
                'first_name': 'Randy',
                'last_name': 'Marsh',
                'username': 'randy',
                'email': 'randy@example.com'
            },
            {   
                'id': 2,
                'last_name': 'Cartman',
                'username': 'cartman',
                'email': 'cartman@example.com'
            },
        ]

    def test_(self):        
        users = self.mixin._modelize_list(
            self.data, User,
            allowed_fields=['first_name', 'last_name', 'username', 'email']
        )

        # Assert that ``users`` are instances of User model
        self.assertTrue(isinstance(users[0], User))
        self.assertTrue(isinstance(users[1], User))

        # Assert users[0]'s field
        self.assertEqual(users[0].id, None)
        self.assertEqual(users[0].first_name, 'Randy')
        self.assertEqual(users[0].last_name, 'Marsh')
        self.assertEqual(users[0].username, 'randy')
        self.assertEqual(users[0].email, 'randy@example.com')

        # Assert users[1]'s field
        self.assertEqual(users[1].id, None)
        self.assertEqual(users[1].first_name, '')
        self.assertEqual(users[1].last_name, 'Cartman')
        self.assertEqual(users[1].username, 'cartman')
        self.assertEqual(users[1].email, 'cartman@example.com')


class TestClean(TestCase):
    """
    Tests the ModelValidationMixin._clean method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()

    def test_clean_model(self):
        user = mommy.make(User)
        user.username = '' # Invalid!

        self.assertRaises(
            ValidationError,
            self.mixin._clean,
            user, exclude=None
        )

    def test_clean_models(self):
        users = mommy.make(User, _quantity=2)
        users[1].username = '' # Invalid!

        self.assertRaises(
            ValidationError,
            self.mixin._clean,
            users, exclude=None,
        )


class TestCleanModel(TestCase):
    """
    Tests the ModelValidationMixin._clean_model method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()

    def test_ValidationError(self):
        # exclude = None
        # Invalid values to fields should raise ValidationError
        user = mommy.make(User)
        user.username = '' # Invalid!
        user.email = 'randy@example.com'

        self.assertRaises(
            ValidationError,
            self.mixin._clean_model,
            user,
            exclude=None,
        )

    def test_all_good(self):
        # exclude=None
        # All values are valid
        user = mommy.make(User)
        user.username = 'randy'
        user.email = 'randy@example.com'

        self.mixin._clean_model(user, exclude=None)
        assert True

    def test_errors_but_exclude(self):
        # exclude = ['username']
        # I exclude the ``username`` field from cleaning. Therefore an invalid
        # value on ``username`` will not raise an exception
        user = mommy.make(User)
        user.username = '' # Invalid!
        user.email = 'randy@example.com'

        self.mixin._clean_model(user, exclude=['username'])
        assert True


class TestCleanModels(TestCase):
    """
    Tests the ModelValidationMixin._clean_models method
    """
    def setUp(self):
        self.mixin = ModelValidationMixin()

    def test_ValidationError(self):
        # Invalid value on a field of one of the model instances, should raise
        # a ValidationError
        users = mommy.make(User, _quantity=2)

        # Setting an invalid value on user[1]'s username
        users[1].username = ''

        self.assertRaises(
            ValidationError,
            self.mixin._clean_models,
            users, 
            exclude=None
        )

    def test_errors_but_exclude(self):
        # Invalid value on field ``username``. However I exclude the field from
        # cleaning, so no exception is raised
        users = mommy.make(User, _quantity=2)

        # Setting an invalid value on user[1]'s username
        users[1].username = ''

        self.mixin._clean_models(users, exclude=['username'])
        assert True
