"""tests/test_middleware.py.

Tests the middleware integrated into IZIR

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
import pytest
from falcon.request import SimpleCookie

import izi
from izi.exceptions import SessionNotFound
from izi.middleware import CORSMiddleware, LogMiddleware, SessionMiddleware
from izi.store import InMemoryStore

api = izi.API(__name__)

# Fix flake8 undefined names (F821)
__izi__ = __izi__  # noqa


def test_session_middleware():
    @izi.get()
    def count(request):
        session = request.context['session']
        counter = session.get('counter', 0) + 1
        session['counter'] = counter
        return counter

    def get_cookies(response):
        simple_cookie = SimpleCookie(response.headers_dict['set-cookie'])
        return {morsel.key: morsel.value for morsel in simple_cookie.values()}

    # Add middleware
    session_store = InMemoryStore()
    middleware = SessionMiddleware(session_store, cookie_name='test-sid')
    __izi__.http.add_middleware(middleware)

    # Get cookies from response
    response = izi.test.get(api, '/count')
    cookies = get_cookies(response)

    # Assert session cookie has been set and session exists in session store
    assert 'test-sid' in cookies
    sid = cookies['test-sid']
    assert session_store.exists(sid)
    assert session_store.get(sid) == {'counter': 1}

    # Assert session persists throughout the requests
    headers = {'Cookie': 'test-sid={}'.format(sid)}
    assert izi.test.get(api, '/count', headers=headers).data == 2
    assert session_store.get(sid) == {'counter': 2}

    # Assert a non-existing session cookie gets ignored
    headers = {'Cookie': 'test-sid=foobarfoo'}
    response = izi.test.get(api, '/count', headers=headers)
    cookies = get_cookies(response)
    assert response.data == 1
    assert not session_store.exists('foobarfoo')
    assert cookies['test-sid'] != 'foobarfoo'


def test_logging_middleware():
    output = []

    class Logger(object):
        def info(self, content):
            output.append(content)

    @izi.middleware_class()
    class CustomLogger(LogMiddleware):
        def __init__(self, logger=Logger()):
            super().__init__(logger=logger)

    @izi.get()
    def test(request):
        return 'data'

    izi.test.get(api, '/test')
    assert output[0] == 'Requested: GET /test None'
    assert len(output[1]) > 0


def test_cors_middleware(izi_api):
    izi_api.http.add_middleware(CORSMiddleware(izi_api, max_age=10))

    @izi.get('/demo', api=izi_api)
    def get_demo():
        return {'result': 'Hello World'}

    @izi.get('/demo/{param}', api=izi_api)
    def get_demo(param):
        return {'result': 'Hello {0}'.format(param)}

    @izi.post('/demo', api=izi_api)
    def post_demo(name: 'your name'):
        return {'result': 'Hello {0}'.format(name)}

    @izi.put('/demo/{param}', api=izi_api)
    def get_demo(param, name):
        old_name = param
        new_name = name
        return {'result': 'Goodbye {0} ... Hello {1}'.format(old_name, new_name)}

    @izi.delete('/demo/{param}', api=izi_api)
    def get_demo(param):
        return {'result': 'Goodbye {0}'.format(param)}

    assert izi.test.get(izi_api, '/demo').data == {'result': 'Hello World'}
    assert izi.test.get(izi_api, '/demo/Mir').data == {'result': 'Hello Mir'}
    assert izi.test.post(izi_api, '/demo', name='Mundo')
    assert izi.test.put(izi_api, '/demo/Carl', name='Junior').data == {'result': 'Goodbye Carl ... Hello Junior'}
    assert izi.test.delete(izi_api, '/demo/Cruel_World').data == {'result': 'Goodbye Cruel_World'}

    response = izi.test.options(izi_api, '/demo')
    methods = response.headers_dict['access-control-allow-methods'].replace(' ', '')
    allow = response.headers_dict['allow'].replace(' ', '')
    assert set(methods.split(',')) == set(['OPTIONS', 'GET', 'POST'])
    assert set(allow.split(',')) == set(['OPTIONS', 'GET', 'POST'])

    response = izi.test.options(izi_api, '/demo/1')
    methods = response.headers_dict['access-control-allow-methods'].replace(' ', '')
    allow = response.headers_dict['allow'].replace(' ', '')
    assert set(methods.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert set(allow.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert response.headers_dict['access-control-max-age'] == '10'

    response = izi.test.options(izi_api, '/v1/demo/1')
    methods = response.headers_dict['access-control-allow-methods'].replace(' ', '')
    allow = response.headers_dict['allow'].replace(' ', '')
    assert set(methods.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert set(allow.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert response.headers_dict['access-control-max-age'] == '10'

    response = izi.test.options(izi_api, '/v1/demo/123e4567-midlee89b-12d3-a456-426655440000')
    methods = response.headers_dict['access-control-allow-methods'].replace(' ', '')
    allow = response.headers_dict['allow'].replace(' ', '')
    assert set(methods.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert set(allow.split(',')) == set(['OPTIONS', 'GET', 'DELETE', 'PUT'])
    assert response.headers_dict['access-control-max-age'] == '10'
