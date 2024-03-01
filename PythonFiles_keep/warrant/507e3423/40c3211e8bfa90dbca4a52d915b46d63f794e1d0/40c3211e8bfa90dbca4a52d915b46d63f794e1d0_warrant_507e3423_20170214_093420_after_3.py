from mock import patch, MagicMock

from botocore.exceptions import ClientError

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, signals
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TransactionTestCase
from django.test.client import RequestFactory
from django.utils.six import iteritems

from cognito.django.backend import CognitoUserPoolAuthBackend
from cognito import User as CognitoUser


class AuthTests(TransactionTestCase):
    def set_tokens(self, mock_cognito_user):
        mock_cognito_user.access_token = 'accesstoken'
        mock_cognito_user.id_token = 'idtoken'
        mock_cognito_user.refresh_token = 'refreshtoken'

    def create_mock_user_obj(self, **kwargs):
        """
        Create a mock UserObj
        :param: kwargs containing desired attrs
        :return: returns mock UserObj
        """
        mock_user_obj = MagicMock(
            user_status=kwargs.pop('user_status', 'CONFIRMED'),
            username=kwargs.pop('access_token', 'testuser'),
            email=kwargs.pop('email', 'test@email.com'),
            given_name=kwargs.pop('given_name', 'FirstName'),
            family_name=kwargs.pop('family_name', 'LastName'),
        )
        for k, v in kwargs.iteritems():
            setattr(mock, k, v)

        return mock_user_obj

    def setup_mock_user(self, mock_cognito_user):
        """
        Configure mocked Cognito User
        :param mock_cognito_user: mock Cognito User
        """
        mock_cognito_user.return_value = mock_cognito_user
        self.set_tokens(mock_cognito_user)

        mock_user_obj = self.create_mock_user_obj()
        mock_cognito_user.get_user.return_value = mock_user_obj

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_user_authentication(self, mock_cognito_user):
        self.setup_mock_user(mock_cognito_user)

        user = authenticate(username='testuser',
                            password='password')

        self.assertIsNotNone(user)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_user_authentication_wrong_password(self, mock_cognito_user):
        mock_cognito_user.return_value = mock_cognito_user
        mock_cognito_user.authenticate.side_effect = ClientError(
            {
                'Error': 
                    {
                        'Message': u'Incorrect username or password.', 'Code': u'NotAuthorizedException'
                    }
            },
            'AdminInitiateAuth')
        user = authenticate(username='username',
                            password='wrongpassword')

        self.assertIsNone(user)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_user_authentication_wrong_username(self, mock_cognito_user):
        mock_cognito_user.return_value = mock_cognito_user
        mock_cognito_user.authenticate.side_effect = ClientError(
            {
                'Error': 
                    {
                        'Message': u'Incorrect username or password.', 'Code': u'NotAuthorizedException'
                    }
            },
            'AdminInitiateAuth')
        user = authenticate(username='wrongusername',
                            password='password')

        self.assertIsNone(user)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_client_login(self, mock_cognito_user):
        self.setup_mock_user(mock_cognito_user)

        user = self.client.login(username='testuser',
                                 password='password')
        self.assertIsNotNone(user)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_new_user_created(self, mock_cognito_user):
        self.setup_mock_user(mock_cognito_user)

        User = get_user_model()
        self.assertEqual(User.objects.count(), 0) 

        user = authenticate(username='testuser',
                            password='password')

        self.assertEqual(User.objects.count(), 1) 
        self.assertEqual(user.username, 'testuser')

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_existing_user_updated(self, mock_cognito_user):
        self.setup_mock_user(mock_cognito_user)

        User = get_user_model()
        existing_user = User.objects.create(username='testuser', email='None')
        user = authenticate(username='testuser',
                            password='password')
        self.assertEqual(user.id, existing_user.id)
        self.assertNotEqual(user.email, existing_user)
        self.assertEqual(User.objects.count(), 1)

        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, user.email)
        self.assertEqual(updated_user.id, user.id)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_existing_user_updated_disabled_create_unknown_user(self, mock_cognito_user):
        class AlternateCognitoUserPoolAuthBackend(CognitoUserPoolAuthBackend):
            create_unknown_user = False

        self.setup_mock_user(mock_cognito_user)

        User = get_user_model()
        existing_user = User.objects.create(username='testuser', email='None')

        backend = AlternateCognitoUserPoolAuthBackend()
        user = backend.authenticate(username='testuser',
                            password='password')
        self.assertEqual(user.id, existing_user.id)
        self.assertNotEqual(user.email, existing_user)
        self.assertEqual(User.objects.count(), 1)

        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, user.email)
        self.assertEqual(updated_user.id, user.id)

    @patch('cognito.django.backend.CognitoUser', autospec=True)
    def test_user_not_found_disabled_create_unknown_user(self, mock_cognito_user):
        class AlternateCognitoUserPoolAuthBackend(CognitoUserPoolAuthBackend):
            create_unknown_user = False

        self.setup_mock_user(mock_cognito_user)

        backend = AlternateCognitoUserPoolAuthBackend()
        user = backend.authenticate(username='testuser',
                            password='password')

        self.assertIsNone(user)

    @patch('cognito.django.backend.CognitoUser')
    def test_inactive_user(self, mock_cognito_user):
        """
        Check that inactive users cannot login.
        In our case, a user is considered inactive if their
        user status in Cognito is 'ARCHIVED' or 'COMPROMISED' or 'UNKNOWN'
        """
        mock_cognito_user.return_value = mock_cognito_user
        mock_user_obj = MagicMock()
        mock_user_obj.user_status = 'COMPROMISED'
        mock_cognito_user.get_user.return_value = mock_user_obj
        user = authenticate(username=settings.COGNITO_TEST_USERNAME,
                            password=settings.COGNITO_TEST_PASSWORD)
        self.assertIsNone(user)

        mock_user_obj.user_status = 'ARCHIVED'
        mock_cognito_user.get_user.return_value = mock_user_obj
        user = authenticate(username=settings.COGNITO_TEST_USERNAME,
                            password=settings.COGNITO_TEST_PASSWORD)
        self.assertIsNone(user)

        mock_user_obj.user_status = 'UNKNOWN'
        mock_cognito_user.get_user.return_value = mock_user_obj
        user = authenticate(username=settings.COGNITO_TEST_USERNAME,
                            password=settings.COGNITO_TEST_PASSWORD)
        self.assertIsNone(user)

    def test_add_user_tokens(self):
        User = get_user_model()
        user = User.objects.create(username=settings.COGNITO_TEST_USERNAME)
        setattr(user, 'access_token', 'access_token_value')
        setattr(user, 'id_token', 'id_token_value')
        setattr(user, 'refresh_token', 'refresh_token_value')

        request = RequestFactory().get('/login')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        signals.user_logged_in.send(sender=user.__class__, request=request, user=user)

        self.assertEqual(request.session['ACCESS_TOKEN'], 'access_token_value')
        self.assertEqual(request.session['ID_TOKEN'], 'id_token_value')
        self.assertEqual(request.session['REFRESH_TOKEN'], 'refresh_token_value')
