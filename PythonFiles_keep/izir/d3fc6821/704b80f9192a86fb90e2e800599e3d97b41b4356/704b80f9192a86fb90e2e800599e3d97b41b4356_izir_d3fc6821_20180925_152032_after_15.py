"""tests/test_directives.py.

Tests to ensure that directives interact in the anticipated manner

Copyright (C) 2018 DiepDT-IZIGlobal

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
from base64 import b64encode

import pytest

import izi

api = izi.API(__name__)

# Fix flake8 undefined names (F821)
__izi__ = __izi__  # noqa


def test_timer():
    """Tests that the timer directive outputs the correct format, and automatically attaches itself to an API"""
    timer = izi.directives.Timer()
    assert isinstance(timer.start, float)
    assert isinstance(float(timer), float)
    assert isinstance(int(timer), int)

    timer = izi.directives.Timer(3)
    assert isinstance(timer.start, float)
    assert isinstance(float(timer), float)
    assert isinstance(int(timer), int)
    assert isinstance(str(timer), str)
    assert isinstance(repr(timer), str)
    assert float(timer) < timer.start

    @izi.get()
    @izi.local()
    def timer_tester(izi_timer):
        return izi_timer

    assert isinstance(izi.test.get(api, 'timer_tester').data, float)
    assert isinstance(timer_tester(), izi.directives.Timer)


def test_module():
    """Test to ensure the module directive automatically includes the current API's module"""
    @izi.get()
    def module_tester(izi_module):
        return izi_module.__name__

    assert izi.test.get(api, 'module_tester').data == api.module.__name__


def test_api():
    """Ensure the api correctly gets passed onto a izi API function based on a directive"""
    @izi.get()
    def api_tester(izi_api):
        return izi_api == api

    assert izi.test.get(api, 'api_tester').data is True


def test_documentation():
    """Test documentation directive"""
    assert 'handlers' in izi.directives.documentation(api=api)


def test_api_version():
    """Ensure that it's possible to get the current version of an API based on a directive"""
    @izi.get(versions=1)
    def version_tester(izi_api_version):
        return izi_api_version

    assert izi.test.get(api, 'v1/version_tester').data == 1


def test_current_api():
    """Ensure that it's possible to retrieve methods from the same version of the API"""
    @izi.get(versions=1)
    def first_method():
        return "Success"

    @izi.get(versions=1)
    def version_call_tester(izi_current_api):
        return izi_current_api.first_method()

    assert izi.test.get(api, 'v1/version_call_tester').data == 'Success'

    @izi.get()
    def second_method():
        return "Unversioned"

    @izi.get(versions=2)  # noqa
    def version_call_tester(izi_current_api):
        return izi_current_api.second_method()

    assert izi.test.get(api, 'v2/version_call_tester').data == 'Unversioned'

    @izi.get(versions=3)  # noqa
    def version_call_tester(izi_current_api):
        return izi_current_api.first_method()

    with pytest.raises(AttributeError):
        izi.test.get(api, 'v3/version_call_tester').data


def test_user():
    """Ensure that it's possible to get the current authenticated user based on a directive"""
    user = 'test_user'
    password = 'super_secret'

    @izi.get(requires=izi.authentication.basic(izi.authentication.verify(user, password)))
    def authenticated_hello(izi_user):
        return izi_user

    token = b64encode('{0}:{1}'.format(user, password).encode('utf8')).decode('utf8')
    assert izi.test.get(api, 'authenticated_hello', headers={'Authorization': 'Basic {0}'.format(token)}).data == user


def test_session_directive():
    """Ensure that it's possible to retrieve the session withing a request using the built-in session directive"""
    @izi.request_middleware()
    def add_session(request, response):
        request.context['session'] = {'test': 'data'}

    @izi.local()
    @izi.get()
    def session_data(izi_session):
        return izi_session

    assert session_data() is None
    assert izi.test.get(api, 'session_data').data == {'test': 'data'}


def test_named_directives():
    """Ensure that it's possible to attach directives to named parameters"""
    @izi.get()
    def test(time: izi.directives.Timer=3):
        return time

    assert isinstance(test(1), int)

    test = izi.local()(test)
    assert isinstance(test(), izi.directives.Timer)


def test_local_named_directives():
    """Ensure that it's possible to attach directives to local function calling"""
    @izi.local()
    def test(time: __izi__.directive('timer')=3):
        return time

    assert isinstance(test(), izi.directives.Timer)

    @izi.local(directives=False)
    def test(time: __izi__.directive('timer')=3):
        return time

    assert isinstance(test(3), int)


def test_named_directives_by_name():
    """Ensure that it's possible to attach directives to named parameters using only the name of the directive"""
    @izi.get()
    @izi.local()
    def test(time: __izi__.directive('timer')=3):
        return time

    assert isinstance(test(), izi.directives.Timer)


def test_per_api_directives():
    """Test to ensure it's easy to define a directive within an API"""
    @izi.directive(apply_globally=False)
    def test(default=None, **kwargs):
        return default

    @izi.get()
    def my_api_method(izi_test='heyyy'):
        return izi_test

    assert izi.test.get(api, 'my_api_method').data == 'heyyy'


def test_user_directives():
    """Test the user directives functionality, to ensure it will provide the set user object"""
    @izi.get()  # noqa
    def try_user(user: izi.directives.user):
        return user

    assert izi.test.get(api, 'try_user').data is None

    @izi.get(requires=izi.authentication.basic(izi.authentication.verify('Tim', 'Custom password')))  # noqa
    def try_user(user: izi.directives.user):
        return user

    token = b'Basic ' + b64encode('{0}:{1}'.format('Tim', 'Custom password').encode('utf8'))
    assert izi.test.get(api, 'try_user', headers={'Authorization': token}).data == 'Tim'


def test_directives(izi_api):
    """Test to ensure cors directive works as expected"""
    assert izi.directives.cors('google.com') == 'google.com'

    @izi.get(api=izi_api)
    def cors_supported(cors: izi.directives.cors="*"):
        return True

    assert izi.test.get(izi_api, 'cors_supported').headers_dict['Access-Control-Allow-Origin'] == '*'
