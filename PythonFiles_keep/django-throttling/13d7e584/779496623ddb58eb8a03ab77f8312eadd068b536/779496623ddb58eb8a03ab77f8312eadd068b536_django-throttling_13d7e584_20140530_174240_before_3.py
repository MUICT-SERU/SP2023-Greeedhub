'''
Run test:
    python manage.py test app
    python manage.py test app --settings=example.alt_settings
'''
from django.test.client                 import Client, RequestFactory
from django.test                        import TestCase
from django.contrib.auth.models         import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test.utils                  import override_settings
from django.conf                        import settings
from throttling.models import Access, Consumer
from throttling.consts import THROTTLING_NUMBER_OF_REQUESTS, THROTTLING_INTERVAL
from throttling.consts import THROTTLING_OPTIONS, THROTTLING_STATUS_CODE
from userroles.models import set_user_role
from userroles        import roles


print "Settings:"
print "THROTTLING_OPTIONS =",            THROTTLING_OPTIONS
print "THROTTLING_STATUS_CODE =",        THROTTLING_STATUS_CODE
print "THROTTLING_INTERVAL =",           THROTTLING_INTERVAL
print "THROTTLING_NUMBER_OF_REQUESTS =", THROTTLING_NUMBER_OF_REQUESTS


class ThrottlingTest(TestCase):
    
    def setUp(self):
        self.user = self.create_user('username')
    
    def create_user(self, username):
        return User.objects.create_user(username, username, username)
    
    def assertStatus(self, url, status, kwargs={}, client=None, repeat=1, login=None):
        if not client: 
            client = Client()
        if login:
            client.login(username=login.username, password=login.username)
        for i in range(repeat):
            response = client.get(url, kwargs)
            self.assertEqual( response.status_code, status )
    
    def test_expiration_date(self):
        pass
        
    def test_view_without_throttle(self):
        url = '/view_without_throttle'
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS )
        self.assertStatus( url, 200 )
            
    def test_view_with_throttle(self):
        url = '/view_with_throttle'
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS )
        self.assertStatus( url, THROTTLING_STATUS_CODE )
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS, login=self.user)
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )
        self.assertStatus( url, THROTTLING_STATUS_CODE )
        
    def test_view_with_throttle_per_anonymous(self):
        url = '/view_with_throttle_per_anonymous'
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS )
        self.assertStatus( url, THROTTLING_STATUS_CODE )
        
    def test_view_with_throttle_all_anonymous(self):
        url = '/view_with_throttle_all_anonymous'
        client = Client(REMOTE_ADDR="127.0.0.1")
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS, client=client )
        self.assertStatus( url, THROTTLING_STATUS_CODE, client=client )
        client = Client(REMOTE_ADDR="127.0.0.2")
        self.assertStatus( url, THROTTLING_STATUS_CODE, client=client )
        self.assertStatus( url, 200, login=self.user )
        
    def test_view_with_throttle_all_users(self):
        url = '/view_with_throttle_all_users'
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS )
        self.assertStatus( url, THROTTLING_STATUS_CODE )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )
        
    def test_view_with_throttle_role(self):
        url = '/view_with_throttle_role'
        self.assertStatus( url, THROTTLING_STATUS_CODE )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )
        set_user_role( self.user, roles.senior_developer )
        self.assertStatus( url, 200, login=self.user, repeat=THROTTLING_NUMBER_OF_REQUESTS-2 )
        set_user_role( self.user, roles.junior_developer )
        self.assertStatus( url, 200, login=self.user )
        set_user_role( self.user, roles.developer )
        self.assertStatus( url, 200, login=self.user )
        set_user_role( self.user, roles.senior_developer )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )     
        set_user_role( self.user, roles.junior_developer )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )        
        set_user_role( self.user, roles.developer )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )        
        set_user_role( self.user, roles.other )
        self.assertStatus( url, 200, login=self.user )
        user = self.create_user('other')
        set_user_role( user, roles.developer )
        self.assertStatus( url, 200, login=user )
        
    def test_view_with_throttle_group(self):
        url = "/view_with_throttle_group"
        group = Group.objects.create(name='groupname')
        self.user.groups.add( group )
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS, login=self.user )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )
        self.assertStatus( url, 200 )
        user = self.create_user('other')
        self.assertStatus( url, 200, login=user )
        user.groups.add( group )
        self.assertStatus( url, 200, login=user )
        
    def test_view_with_throttle_all_in_group(self):
        url = "/view_with_throttle_all_in_group"
        group = Group.objects.create(name='groupname')
        self.user.groups.add( group )
        self.assertStatus( url, 200, repeat=THROTTLING_NUMBER_OF_REQUESTS, login=self.user )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=self.user )
        self.assertStatus( url, 200 )
        user = self.create_user('other')
        self.assertStatus( url, 200, login=user )
        user.groups.add( group )
        self.assertStatus( url, THROTTLING_STATUS_CODE, login=user )
        
