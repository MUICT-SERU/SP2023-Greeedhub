"""tests/test_decorators.py.

Tests the decorators that power izis core functionality

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
import json
import os
import sys
from unittest import mock
from collections import namedtuple

import falcon
import pytest
import requests
from falcon.testing import StartResponseMock, create_environ
from marshmallow import Schema, fields

import izi
from izi._async import coroutine
from izi.exceptions import InvalidTypeData

from .constants import BASE_DIRECTORY

api = izi.API(__name__)
module = sys.modules[__name__]

# Fix flake8 undefined names (F821)
__izi__ = __izi__  # noqa
__izi_wsgi__ = __izi_wsgi__  # noqa


def test_basic_call():
    """The most basic Happy-Path test for IZIR APIs"""
    @izi.call()
    def hello_world():
        return "Hello World!"

    assert hello_world() == "Hello World!"
    assert hello_world.interface.http

    assert izi.test.get(api, '/hello_world').data == "Hello World!"
    assert izi.test.get(module, '/hello_world').data == "Hello World!"


def test_basic_call_on_method(izi_api):
    """Test to ensure the most basic call still works if applied to a method"""
    class API(object):

        @izi.call(api=izi_api)
        def hello_world(self=None):
            return "Hello World!"

    api_instance = API()
    assert api_instance.hello_world.interface.http
    assert api_instance.hello_world() == 'Hello World!'
    assert izi.test.get(izi_api, '/hello_world').data == "Hello World!"

    class API(object):

        def hello_world(self):
            return "Hello World!"

    api_instance = API()

    @izi.call(api=izi_api)
    def hello_world():
        return api_instance.hello_world()

    assert api_instance.hello_world() == 'Hello World!'
    assert izi.test.get(izi_api, '/hello_world').data == "Hello World!"

    class API(object):

        def __init__(self):
            izi.call(api=izi_api)(self.hello_world_method)

        def hello_world_method(self):
            return "Hello World!"

    api_instance = API()

    assert api_instance.hello_world_method() == 'Hello World!'
    assert izi.test.get(izi_api, '/hello_world_method').data == "Hello World!"


def test_single_parameter(izi_api):
    """Test that an api with a single parameter interacts as desired"""
    @izi.call(api=izi_api)
    def echo(text):
        return text

    assert echo('Embrace') == 'Embrace'
    assert echo.interface.http
    with pytest.raises(TypeError):
        echo()

    assert izi.test.get(izi_api, 'echo', text="Hello").data == "Hello"
    assert 'required' in izi.test.get(izi_api, '/echo').data['errors']['text'].lower()


def test_on_invalid_transformer():
    """Test to ensure it is possible to transform data when data is invalid"""
    @izi.call(on_invalid=lambda data: 'error')
    def echo(text):
        return text
    assert izi.test.get(api, '/echo').data == 'error'


    def handle_error(data, request, response):
        return 'errored'

    @izi.call(on_invalid=handle_error)
    def echo2(text):
        return text
    assert izi.test.get(api, '/echo2').data == 'errored'


def test_on_invalid_format():
    """Test to ensure it's possible to change the format based on a validation error"""
    @izi.get(output_invalid=izi.output_format.json, output=izi.output_format.file)
    def echo(text):
        return text

    assert isinstance(izi.test.get(api, '/echo').data, dict)

    def smart_output_type(response, request):
        if response and request:
            return 'application/json'

    @izi.format.content_type(smart_output_type)
    def output_formatter(data, request, response):
        return izi.output_format.json((data, request and True, response and True))

    @izi.get(output_invalid=output_formatter, output=izi.output_format.file)
    def echo2(text):
        return text

    assert isinstance(izi.test.get(api, '/echo2').data, (list, tuple))


def test_smart_redirect_routing():
    """Test to ensure you can easily redirect to another method without an actual redirect"""
    @izi.get()
    def implementation_1():
        return 1

    @izi.get()
    def implementation_2():
        return 2

    @izi.get()
    def smart_route(implementation: int):
        if implementation == 1:
            return implementation_1
        elif implementation == 2:
            return implementation_2
        else:
            return "NOT IMPLEMENTED"

    assert izi.test.get(api, 'smart_route', implementation=1).data == 1
    assert izi.test.get(api, 'smart_route', implementation=2).data == 2
    assert izi.test.get(api, 'smart_route', implementation=3).data == "NOT IMPLEMENTED"


def test_custom_url():
    """Test to ensure that it's possible to have a route that differs from the function name"""
    @izi.call('/custom_route')
    def method_name():
        return 'works'

    assert izi.test.get(api, 'custom_route').data == 'works'


def test_api_auto_initiate():
    """Test to ensure that IZIR automatically exposes a wsgi server method"""
    assert isinstance(__izi_wsgi__(create_environ('/non_existant'), StartResponseMock()), (list, tuple))


def test_parameters():
    """Tests to ensure that IZIR can easily handle multiple parameters with multiple types"""
    @izi.call()
    def multiple_parameter_types(start, middle: izi.types.text, end: izi.types.number=5, **kwargs):
        return 'success'

    assert izi.test.get(api, 'multiple_parameter_types', start='start', middle='middle', end=7).data == 'success'
    assert izi.test.get(api, 'multiple_parameter_types', start='start', middle='middle').data == 'success'
    assert izi.test.get(api, 'multiple_parameter_types', start='start', middle='middle', other="yo").data == 'success'

    nan_test = izi.test.get(api, 'multiple_parameter_types', start='start', middle='middle', end='NAN').data
    assert 'Invalid' in nan_test['errors']['end']


def test_raise_on_invalid():
    """Test to ensure izi correctly respects a request to allow validations errors to pass through as exceptions"""
    @izi.get(raise_on_invalid=True)
    def my_handler(argument_1: int):
        return True

    with pytest.raises(Exception):
        izi.test.get(api, 'my_handler', argument_1='hi')

    assert izi.test.get(api, 'my_handler', argument_1=1)


def test_range_request():
    """Test to ensure that requesting a range works as expected"""
    @izi.get(output=izi.output_format.png_image)
    def image():
        return 'artwork/logo.png'

    assert izi.test.get(api, 'image', headers={'range': 'bytes=0-100'})
    assert izi.test.get(api, 'image', headers={'range': 'bytes=0--1'})

def test_parameters_override():
    """Test to ensure the parameters override is handled as expected"""
    @izi.get(parameters=('parameter1', 'parameter2'))
    def test_call(**kwargs):
        return kwargs

    assert izi.test.get(api, 'test_call', parameter1='one', parameter2='two').data == {'parameter1': 'one',
                                                                                       'parameter2': 'two'}


def test_parameter_injection():
    """Tests that izi correctly auto injects variables such as request and response"""
    @izi.call()
    def inject_request(request):
        return request and 'success'
    assert izi.test.get(api, 'inject_request').data == 'success'

    @izi.call()
    def inject_response(response):
        return response and 'success'
    assert izi.test.get(api, 'inject_response').data == 'success'

    @izi.call()
    def inject_both(request, response):
        return request and response and 'success'
    assert izi.test.get(api, 'inject_both').data == 'success'

    @izi.call()
    def wont_appear_in_kwargs(**kwargs):
        return 'request' not in kwargs and 'response' not in kwargs and 'success'
    assert izi.test.get(api, 'wont_appear_in_kwargs').data == 'success'


def test_method_routing():
    """Test that all izis HTTP routers correctly route methods to the correct handler"""
    @izi.get()
    def method_get():
        return 'GET'

    @izi.post()
    def method_post():
        return 'POST'

    @izi.connect()
    def method_connect():
        return 'CONNECT'

    @izi.delete()
    def method_delete():
        return 'DELETE'

    @izi.options()
    def method_options():
        return 'OPTIONS'

    @izi.put()
    def method_put():
        return 'PUT'

    @izi.trace()
    def method_trace():
        return 'TRACE'

    assert izi.test.get(api, 'method_get').data == 'GET'
    assert izi.test.post(api, 'method_post').data == 'POST'
    assert izi.test.connect(api, 'method_connect').data == 'CONNECT'
    assert izi.test.delete(api, 'method_delete').data == 'DELETE'
    assert izi.test.options(api, 'method_options').data == 'OPTIONS'
    assert izi.test.put(api, 'method_put').data == 'PUT'
    assert izi.test.trace(api, 'method_trace').data == 'TRACE'

    @izi.call(accept=('GET', 'POST'))
    def accepts_get_and_post():
        return 'success'

    assert izi.test.get(api, 'accepts_get_and_post').data == 'success'
    assert izi.test.post(api, 'accepts_get_and_post').data == 'success'
    assert 'method not allowed' in izi.test.trace(api, 'accepts_get_and_post').status.lower()


def test_not_found():
    """Test to ensure the not_found decorator correctly routes 404s to the correct handler"""
    @izi.not_found()
    def not_found_handler():
        return "Not Found"

    result = izi.test.get(api, '/does_not_exist/yet')
    assert result.data == "Not Found"
    assert result.status == falcon.HTTP_NOT_FOUND

    @izi.not_found(versions=10)  # noqa
    def not_found_handler(response):
        response.status = falcon.HTTP_OK
        return {'look': 'elsewhere'}

    result = izi.test.get(api, '/v10/does_not_exist/yet')
    assert result.data == {'look': 'elsewhere'}
    assert result.status == falcon.HTTP_OK

    result = izi.test.get(api, '/does_not_exist/yet')
    assert result.data == "Not Found"
    assert result.status == falcon.HTTP_NOT_FOUND

    del api.http._not_found_handlers


def test_not_found_with_extended_api():
    """Test to ensure the not_found decorator works correctly when the API is extended"""
    @izi.extend_api()
    def extend_with():
        import tests.module_fake
        return (tests.module_fake, )

    assert izi.test.get(api, '/does_not_exist/yet').data is True

def test_versioning():
    """Ensure that IZIR correctly routes API functions based on version"""
    @izi.get('/echo')
    def echo(text):
        return "Not Implemented"

    @izi.get('/echo', versions=1)  # noqa
    def echo(text):
        return text

    @izi.get('/echo', versions=range(2, 4))  # noqa
    def echo(text):
        return "Echo: {text}".format(**locals())

    @izi.get('/echo', versions=7)  # noqa
    def echo(text, api_version):
        return api_version

    @izi.get('/echo', versions='8')  # noqa
    def echo(text, api_version):
        return api_version

    @izi.get('/echo', versions=False)  # noqa
    def echo(text):
        return "No Versions"

    with pytest.raises(ValueError):
        @izi.get('/echo', versions='eight')  # noqa
        def echo(text, api_version):
            return api_version

    assert izi.test.get(api, 'v1/echo', text="hi").data == 'hi'
    assert izi.test.get(api, 'v2/echo', text="hi").data == "Echo: hi"
    assert izi.test.get(api, 'v3/echo', text="hi").data == "Echo: hi"
    assert izi.test.get(api, 'echo', text="hi", api_version=3).data == "Echo: hi"
    assert izi.test.get(api, 'echo', text="hi", headers={'X-API-VERSION': '3'}).data == "Echo: hi"
    assert izi.test.get(api, 'v4/echo', text="hi").data == "Not Implemented"
    assert izi.test.get(api, 'v7/echo', text="hi").data == 7
    assert izi.test.get(api, 'v8/echo', text="hi").data == 8
    assert izi.test.get(api, 'echo', text="hi").data == "No Versions"
    assert izi.test.get(api, 'echo', text="hi", api_version=3, body={'api_vertion': 4}).data == "Echo: hi"

    with pytest.raises(ValueError):
        izi.test.get(api, 'v4/echo', text="hi", api_version=3)


def test_multiple_version_injection():
    """Test to ensure that the version injected sticks when calling other functions within an API"""
    @izi.get(versions=(1, 2, None))
    def my_api_function(izi_api_version):
        return izi_api_version

    assert izi.test.get(api, 'v1/my_api_function').data == 1
    assert izi.test.get(api, 'v2/my_api_function').data == 2
    assert izi.test.get(api, 'v3/my_api_function').data == 3

    @izi.get(versions=(None, 1))
    @izi.local(version=1)
    def call_other_function(izi_current_api):
        return izi_current_api.my_api_function()

    assert izi.test.get(api, 'v1/call_other_function').data == 1
    assert call_other_function() == 1

    @izi.get(versions=1)
    @izi.local(version=1)
    def one_more_level_of_indirection(izi_current_api):
        return izi_current_api.call_other_function()

    assert izi.test.get(api, 'v1/one_more_level_of_indirection').data == 1
    assert one_more_level_of_indirection() == 1


def test_json_auto_convert():
    """Test to ensure all types of data correctly auto convert into json"""
    @izi.get('/test_json')
    def test_json(text):
        return text
    assert izi.test.get(api, 'test_json', body={'text': 'value'}).data == "value"

    @izi.get('/test_json_body')
    def test_json_body(body):
        return body
    assert izi.test.get(api, 'test_json_body', body=['value1', 'value2']).data == ['value1', 'value2']

    @izi.get(parse_body=False)
    def test_json_body_stream_only(body=None):
        return body
    assert izi.test.get(api, 'test_json_body_stream_only', body=['value1', 'value2']).data is None


def test_error_handling():
    """Test to ensure IZIR correctly handles Falcon errors that are thrown during processing"""
    @izi.get()
    def test_error():
        raise falcon.HTTPInternalServerError('Failed', 'For Science!')

    response = izi.test.get(api, 'test_error')
    assert 'errors' in response.data
    assert response.data['errors']['Failed'] == 'For Science!'


def test_error_handling_builtin_exception():
    """Test to ensure built in exception types errors are handled as expected"""
    def raise_error(value):
        raise KeyError('Invalid value')

    @izi.get()
    def test_error(data: raise_error):
        return True

    response = izi.test.get(api, 'test_error', data=1)
    assert 'errors' in response.data
    assert response.data['errors']['data'] == 'Invalid value'


def test_error_handling_custom():
    """Test to ensure custom exceptions work as expected"""
    class Error(Exception):

        def __str__(self):
            return 'Error'

    def raise_error(value):
        raise Error()

    @izi.get()
    def test_error(data: raise_error):
        return True

    response = izi.test.get(api, 'test_error', data=1)
    assert 'errors' in response.data
    assert response.data['errors']['data'] == 'Error'


def test_return_modifer():
    """Ensures you can modify the output of a IZIR API using -> annotation"""
    @izi.get()
    def hello() -> lambda data: "Hello {0}!".format(data):
        return "world"

    assert izi.test.get(api, 'hello').data == "Hello world!"
    assert hello() == 'world'

    @izi.get(transform=lambda data: "Goodbye {0}!".format(data))
    def hello() -> lambda data: "Hello {0}!".format(data):
        return "world"
    assert izi.test.get(api, 'hello').data == "Goodbye world!"
    assert hello() == 'world'

    @izi.get()
    def hello() -> str:
        return "world"
    assert izi.test.get(api, 'hello').data == "world"
    assert hello() == 'world'

    @izi.get(transform=False)
    def hello() -> lambda data: "Hello {0}!".format(data):
        return "world"

    assert izi.test.get(api, 'hello').data == "world"
    assert hello() == 'world'

    def transform_with_request_data(data, request, response):
        return (data, request and True, response and True)

    @izi.get(transform=transform_with_request_data)
    def hello():
        return "world"

    response = izi.test.get(api, 'hello')
    assert response.data == ['world', True, True]


def test_custom_deserializer_support():
    """Ensure that custom desirializers work as expected"""
    class CustomDeserializer(object):
        def from_string(self, string):
            return 'custom {}'.format(string)

    @izi.get()
    def test_custom_deserializer(text: CustomDeserializer()):
        return text

    assert izi.test.get(api, 'test_custom_deserializer', text='world').data == 'custom world'


def test_marshmallow_support():
    """Ensure that you can use Marshmallow style objects to control input and output validation and transformation"""
    MarshalResult = namedtuple('MarshalResult', ['data', 'errors'])

    class MarshmallowStyleObject(object):
        def dump(self, item):
            if item == 'bad':
                return MarshalResult('', 'problems')
            return MarshalResult('Dump Success', {})

        def load(self, item):
            return ('Load Success', None)

        def loads(self, item):
            return self.load(item)

    schema = MarshmallowStyleObject()

    @izi.get()
    def test_marshmallow_style() -> schema:
        return 'world'

    assert izi.test.get(api, 'test_marshmallow_style').data == "Dump Success"
    assert test_marshmallow_style() == 'world'


    @izi.get()
    def test_marshmallow_style_error() -> schema:
        return 'bad'

    with pytest.raises(InvalidTypeData):
        izi.test.get(api, 'test_marshmallow_style_error')


    @izi.get()
    def test_marshmallow_input(item: schema):
        return item

    assert izi.test.get(api, 'test_marshmallow_input', item='bacon').data == "Load Success"
    assert test_marshmallow_style() == 'world'

    class MarshmallowStyleObjectWithError(object):
        def dump(self, item):
            return 'Dump Success'

        def load(self, item):
            return ('Load Success', {'type': 'invalid'})

        def loads(self, item):
            return self.load(item)

    schema = MarshmallowStyleObjectWithError()

    @izi.get()
    def test_marshmallow_input2(item: schema):
        return item

    assert izi.test.get(api, 'test_marshmallow_input2', item='bacon').data == {'errors': {'item': {'type': 'invalid'}}}

    class MarshmallowStyleField(object):
        def deserialize(self, value):
            return str(value)

    @izi.get()
    def test_marshmallow_input_field(item: MarshmallowStyleField()):
        return item

    assert izi.test.get(api, 'test_marshmallow_input_field', item='bacon').data == 'bacon'


def test_stream_return():
    """Test to ensure that its valid for a izi API endpoint to return a stream"""
    @izi.get(output=izi.output_format.text)
    def test():
        return open(os.path.join(BASE_DIRECTORY, 'README.md'), 'rb')

    assert 'izi' in izi.test.get(api, 'test').data


def test_smart_outputter():
    """Test to ensure that the output formatter can accept request and response arguments"""
    def smart_output_type(response, request):
        if response and request:
            return 'application/json'

    @izi.format.content_type(smart_output_type)
    def output_formatter(data, request, response):
        return izi.output_format.json((data, request and True, response and True))

    @izi.get(output=output_formatter)
    def test():
        return True

    assert izi.test.get(api, 'test').data == [True, True, True]


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_output_format():
    """Test to ensure it's possible to quickly change the default izi output format"""
    old_formatter = api.http.output_format

    @izi.default_output_format()
    def augmented(data):
        return izi.output_format.json(['Augmented', data])

    @izi.get(suffixes=('.js', '/js'), prefixes='/text')
    def hello():
        return "world"

    assert izi.test.get(api, 'hello').data == ['Augmented', 'world']
    assert izi.test.get(api, 'hello.js').data == ['Augmented', 'world']
    assert izi.test.get(api, 'hello/js').data == ['Augmented', 'world']
    assert izi.test.get(api, 'text/hello').data == ['Augmented', 'world']

    @izi.default_output_format()
    def jsonify(data):
        return izi.output_format.json(data)


    api.http.output_format = izi.output_format.text

    @izi.get()
    def my_method():
        return {'Should': 'work'}

    assert izi.test.get(api, 'my_method').data == "{'Should': 'work'}"
    api.http.output_format = old_formatter


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_input_format():
    """Test to ensure it's possible to quickly change the default izi output format"""
    old_format = api.http.input_format('application/json')
    api.http.set_input_format('application/json', lambda a: {'no': 'relation'})

    @izi.get()
    def hello(body):
        return body

    assert izi.test.get(api, 'hello', body={'should': 'work'}).data == {'no': 'relation'}

    @izi.get()
    def hello2(body):
        return body

    assert not izi.test.get(api, 'hello2').data

    api.http.set_input_format('application/json', old_format)


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_specific_input_format():
    """Test to ensure the input formatter can be specified"""
    @izi.get(inputs={'application/json': lambda a: 'formatted'})
    def hello(body):
        return body

    assert izi.test.get(api, 'hello', body={'should': 'work'}).data == 'formatted'


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_content_type_with_parameter():
    """Test a Content-Type with parameter as `application/json charset=UTF-8`
    as described in https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7"""
    @izi.get()
    def demo(body):
        return body

    assert izi.test.get(api, 'demo', body={}, headers={'content-type': 'application/json'}).data == {}
    assert izi.test.get(api, 'demo', body={}, headers={'content-type': 'application/json; charset=UTF-8'}).data == {}


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_middleware():
    """Test to ensure the basic concept of a middleware works as expected"""
    @izi.request_middleware()
    def proccess_data(request, response):
        request.env['SERVER_NAME'] = 'Bacon'

    @izi.response_middleware()
    def proccess_data2(request, response, resource):
        response.set_header('Bacon', 'Yumm')

    @izi.reqresp_middleware()
    def process_data3(request):
        request.env['MEET'] = 'Ham'
        response, resource = yield request
        response.set_header('Ham', 'Buu!!')
        yield response

    @izi.get()
    def hello(request):
        return [
            request.env['SERVER_NAME'],
            request.env['MEET']
        ]

    result = izi.test.get(api, 'hello')
    assert result.data == ['Bacon', 'Ham']
    assert result.headers_dict['Bacon'] == 'Yumm'
    assert result.headers_dict['Ham'] == 'Buu!!'


def test_requires():
    """Test to ensure only if requirements successfully keep calls from happening"""
    def user_is_not_tim(request, response, **kwargs):
        if request.headers.get('USER', '') != 'Tim':
            return True
        return 'Unauthorized'

    @izi.get(requires=user_is_not_tim)
    def hello(request):
        return 'Hi!'

    assert izi.test.get(api, 'hello').data == 'Hi!'
    assert izi.test.get(api, 'hello', headers={'USER': 'Tim'}).data == 'Unauthorized'


def test_extending_api():
    """Test to ensure it's possible to extend the current API from an external file"""
    @izi.extend_api('/fake')
    def extend_with():
        import tests.module_fake
        return (tests.module_fake, )

    @izi.get('/fake/error')
    def my_error():
        import tests.module_fake
        raise tests.module_fake.FakeException()

    assert izi.test.get(api, 'fake/made_up_api').data
    assert izi.test.get(api, 'fake/error').data == True


def test_extending_api_simple():
    """Test to ensure it's possible to extend the current API from an external file with just one API endpoint"""
    @izi.extend_api('/fake_simple')
    def extend_with():
        import tests.module_fake_simple
        return (tests.module_fake_simple, )

    assert izi.test.get(api, 'fake_simple/made_up_hello').data == 'hello'


def test_extending_api_with_exception_handler():
    """Test to ensure it's possible to extend the current API from an external file"""

    from tests.module_fake_simple import FakeSimpleException

    @izi.exception(FakeSimpleException)
    def handle_exception(exception):
        return 'it works!'

    @izi.extend_api('/fake_simple')
    def extend_with():
        import tests.module_fake_simple
        return (tests.module_fake_simple, )

    assert izi.test.get(api, '/fake_simple/exception').data == 'it works!'


def test_extending_api_with_base_url():
    """Test to ensure it's possible to extend the current API with a specified base URL"""
    @izi.extend_api('/fake', base_url='/api')
    def extend_with():
        import tests.module_fake
        return (tests.module_fake, )

    assert izi.test.get(api, '/api/v1/fake/made_up_api').data


def test_extending_api_with_same_path_under_different_base_url():
    """Test to ensure it's possible to extend the current API with the same path under a different base URL"""
    @izi.get()
    def made_up_hello():
        return 'hi'

    @izi.extend_api(base_url='/api')
    def extend_with():
        import tests.module_fake_simple
        return (tests.module_fake_simple, )

    assert izi.test.get(api, '/made_up_hello').data == 'hi'
    assert izi.test.get(api, '/api/made_up_hello').data == 'hello'


def test_cli():
    """Test to ensure the CLI wrapper works as intended"""
    @izi.cli('command', '1.0.0', output=str)
    def cli_command(name: str, value: int):
        return (name, value)

    assert cli_command('Testing', 1) == ('Testing', 1)
    assert izi.test.cli(cli_command, "Bob", 5) == ("Bob", 5)


def test_cli_requires():
    """Test to ensure your can add requirements to a CLI"""
    def requires_fail(**kwargs):
        return {'requirements': 'not met'}

    @izi.cli(output=str, requires=requires_fail)
    def cli_command(name: str, value: int):
        return (name, value)

    assert cli_command('Testing', 1) == ('Testing', 1)
    assert izi.test.cli(cli_command, 'Testing', 1) == {'requirements': 'not met'}


def test_cli_validation():
    """Test to ensure your can add custom validation to a CLI"""
    def contains_either(fields):
        if not fields.get('name', '') and not fields.get('value', 0):
            return {'name': 'must be defined', 'value': 'must be defined'}

    @izi.cli(output=str, validate=contains_either)
    def cli_command(name: str="", value: int=0):
        return (name, value)

    assert cli_command('Testing', 1) == ('Testing', 1)
    assert izi.test.cli(cli_command) == {'name': 'must be defined', 'value': 'must be defined'}
    assert izi.test.cli(cli_command, name='Testing') == ('Testing', 0)


def test_cli_with_defaults():
    """Test to ensure CLIs work correctly with default values"""
    @izi.cli()
    def happy(name: str, age: int, birthday: bool=False):
        if birthday:
            return "Happy {age} birthday {name}!".format(**locals())
        else:
            return "{name} is {age} years old".format(**locals())

    assert happy('IZIR', 1) == "IZIR is 1 years old"
    assert happy('IZIR', 1, True) == "Happy 1 birthday IZIR!"
    assert izi.test.cli(happy, "Bob", 5) == "Bob is 5 years old"
    assert izi.test.cli(happy, "Bob", 5, birthday=True) == "Happy 5 birthday Bob!"


def test_cli_with_izi_types():
    """Test to ensure CLIs work as expected when using izi types"""
    @izi.cli()
    def happy(name: izi.types.text, age: izi.types.number, birthday: izi.types.boolean=False):
        if birthday:
            return "Happy {age} birthday {name}!".format(**locals())
        else:
            return "{name} is {age} years old".format(**locals())

    assert happy('IZIR', 1) == "IZIR is 1 years old"
    assert happy('IZIR', 1, True) == "Happy 1 birthday IZIR!"
    assert izi.test.cli(happy, "Bob", 5) == "Bob is 5 years old"
    assert izi.test.cli(happy, "Bob", 5, birthday=True) == "Happy 5 birthday Bob!"

    @izi.cli()
    def succeed(success: izi.types.smart_boolean=False):
        if success:
            return 'Yes!'
        else:
            return 'No :('

    assert izi.test.cli(succeed) == 'No :('
    assert izi.test.cli(succeed, success=True) == 'Yes!'
    assert 'succeed' in str(__izi__.cli)

    @izi.cli()
    def succeed(success: izi.types.smart_boolean=True):
        if success:
            return 'Yes!'
        else:
            return 'No :('

    assert izi.test.cli(succeed) == 'Yes!'
    assert izi.test.cli(succeed, success='false') == 'No :('

    @izi.cli()
    def all_the(types: izi.types.multiple=[]):
        return types or ['nothing_here']

    assert izi.test.cli(all_the) == ['nothing_here']
    assert izi.test.cli(all_the, types=('one', 'two', 'three')) == ['one', 'two', 'three']

    @izi.cli()
    def all_the(types: izi.types.multiple):
        return types or ['nothing_here']

    assert izi.test.cli(all_the) == ['nothing_here']
    assert izi.test.cli(all_the, 'one', 'two', 'three') == ['one', 'two', 'three']

    @izi.cli()
    def one_of(value: izi.types.one_of(['one', 'two'])='one'):
        return value

    assert izi.test.cli(one_of, value='one') == 'one'
    assert izi.test.cli(one_of, value='two') == 'two'


def test_cli_with_conflicting_short_options():
    """Test to ensure that it's possible to expose a CLI with the same first few letters in option"""
    @izi.cli()
    def test(abe1="Value", abe2="Value2", helper=None):
        return (abe1, abe2)

    assert test() == ('Value', 'Value2')
    assert test('hi', 'there') == ('hi', 'there')
    assert izi.test.cli(test) == ('Value', 'Value2')
    assert izi.test.cli(test, abe1='hi', abe2='there') == ('hi', 'there')


def test_cli_with_directives():
    """Test to ensure it's possible to use directives with izi CLIs"""
    @izi.cli()
    @izi.local()
    def test(izi_timer):
        return float(izi_timer)

    assert isinstance(test(), float)
    assert test(izi_timer=4) == 4
    assert isinstance(izi.test.cli(test), float)


def test_cli_with_class_directives():

    @izi.directive()
    class ClassDirective(object):

        def __init__(self, *args, **kwargs):
            self.test = 1

    @izi.cli()
    @izi.local(skip_directives=False)
    def test(class_directive: ClassDirective):
        return class_directive.test

    assert test() == 1
    assert izi.test.cli(test) == 1

    class TestObject(object):
        is_cleanup_launched = False
        last_exception = None

    @izi.directive()
    class ClassDirectiveWithCleanUp(object):

        def __init__(self, *args, **kwargs):
            self.test_object = TestObject

        def cleanup(self, exception):
            self.test_object.is_cleanup_launched = True
            self.test_object.last_exception = exception

    @izi.cli()
    @izi.local(skip_directives=False)
    def test2(class_directive: ClassDirectiveWithCleanUp):
        return class_directive.test_object.is_cleanup_launched

    assert not izi.test.cli(test2)  # cleanup should be launched after running command
    assert TestObject.is_cleanup_launched
    assert TestObject.last_exception is None
    TestObject.is_cleanup_launched = False
    TestObject.last_exception = None
    assert not test2()
    assert TestObject.is_cleanup_launched
    assert TestObject.last_exception is None

    @izi.cli()
    @izi.local(skip_directives=False)
    def test_with_attribute_error(class_directive: ClassDirectiveWithCleanUp):
        raise class_directive.test_object2

    izi.test.cli(test_with_attribute_error)
    assert TestObject.is_cleanup_launched
    assert isinstance(TestObject.last_exception, AttributeError)
    TestObject.is_cleanup_launched = False
    TestObject.last_exception = None
    try:
        test_with_attribute_error()
        assert False
    except AttributeError:
        assert True
    assert TestObject.is_cleanup_launched
    assert isinstance(TestObject.last_exception, AttributeError)


def test_cli_with_named_directives():
    """Test to ensure you can pass named directives into the cli"""
    @izi.cli()
    @izi.local()
    def test(timer: izi.directives.Timer):
        return float(timer)

    assert isinstance(test(), float)
    assert test(timer=4) == 4
    assert isinstance(izi.test.cli(test), float)


def test_cli_with_output_transform():
    """Test to ensure it's possible to use output transforms with izi CLIs"""
    @izi.cli()
    def test() -> int:
        return '5'

    assert isinstance(test(), str)
    assert isinstance(izi.test.cli(test), int)


    @izi.cli(transform=int)
    def test():
        return '5'

    assert isinstance(test(), str)
    assert isinstance(izi.test.cli(test), int)


def test_cli_with_short_short_options():
    """Test to ensure that it's possible to expose a CLI with 2 very short and similar options"""
    @izi.cli()
    def test(a1="Value", a2="Value2"):
        return (a1, a2)

    assert test() == ('Value', 'Value2')
    assert test('hi', 'there') == ('hi', 'there')
    assert izi.test.cli(test) == ('Value', 'Value2')
    assert izi.test.cli(test, a1='hi', a2='there') == ('hi', 'there')


def test_cli_file_return():
    """Test to ensure that its possible to return a file stream from a CLI"""
    @izi.cli()
    def test():
        return open(os.path.join(BASE_DIRECTORY, 'README.md'), 'rb')

    assert 'izi' in izi.test.cli(test)


def test_local_type_annotation():
    """Test to ensure local type annotation works as expected"""
    @izi.local(raise_on_invalid=True)
    def test(number: int):
        return number

    assert test(3) == 3
    with pytest.raises(Exception):
        test('h')

    @izi.local(raise_on_invalid=False)
    def test(number: int):
        return number

    assert test('h')['errors']

    @izi.local(raise_on_invalid=False, validate=False)
    def test(number: int):
        return number

    assert test('h') == 'h'


def test_local_transform():
    """Test to ensure local type annotation works as expected"""
    @izi.local(transform=str)
    def test(number: int):
        return number

    assert test(3) == '3'


def test_local_on_invalid():
    """Test to ensure local type annotation works as expected"""
    @izi.local(on_invalid=str)
    def test(number: int):
        return number

    assert isinstance(test('h'), str)


def test_local_requires():
    """Test to ensure only if requirements successfully keep calls from happening locally"""
    global_state = False

    def requirement(**kwargs):
        return global_state and 'Unauthorized'

    @izi.local(requires=requirement)
    def hello():
        return 'Hi!'

    assert hello() == 'Hi!'
    global_state = True
    assert hello() == 'Unauthorized'


def test_static_file_support():
    """Test to ensure static file routing works as expected"""
    @izi.static('/static')
    def my_static_dirs():
        return (BASE_DIRECTORY, )

    assert 'izi' in izi.test.get(api, '/static/README.md').data
    assert 'Index' in izi.test.get(api, '/static/tests/data').data
    assert '404' in izi.test.get(api, '/static/NOT_IN_EXISTANCE.md').status


def test_static_jailed():
    """Test to ensure we can't serve from outside static dir"""
    @izi.static('/static')
    def my_static_dirs():
        return ['tests']
    assert '404' in izi.test.get(api, '/static/../README.md').status


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_sink_support():
    """Test to ensure sink URL routers work as expected"""
    @izi.sink('/all')
    def my_sink(request):
        return request.path.replace('/all', '')

    assert izi.test.get(api, '/all/the/things').data == '/the/things'

@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_sink_support_with_base_url():
    """Test to ensure sink URL routers work when the API is extended with a specified base URL"""
    @izi.extend_api('/fake', base_url='/api')
    def extend_with():
        import tests.module_fake
        return (tests.module_fake, )

    assert izi.test.get(api, '/api/fake/all/the/things').data == '/the/things'

def test_cli_with_string_annotation():
    """Test to ensure CLI's work correctly with string annotations"""
    @izi.cli()
    def test(value_1: 'The first value', value_2: 'The second value'=None):
        return True

    assert izi.test.cli(test, True)


def test_cli_with_args():
    """Test to ensure CLI's work correctly when taking args"""
    @izi.cli()
    def test(*values):
        return values

    assert test(1, 2, 3) == (1, 2, 3)
    assert izi.test.cli(test, 1, 2, 3) == ('1', '2', '3')


def test_cli_using_method():
    """Test to ensure that attaching a cli to a class method works as expected"""
    class API(object):

        def __init__(self):
            izi.cli()(self.hello_world_method)

        def hello_world_method(self):
            variable = 'Hello World!'
            return variable

    api_instance = API()
    assert api_instance.hello_world_method() == 'Hello World!'
    assert izi.test.cli(api_instance.hello_world_method) == 'Hello World!'
    assert izi.test.cli(api_instance.hello_world_method, collect_output=False) is None


def test_cli_with_nested_variables():
    """Test to ensure that a cli containing multiple nested variables works correctly"""
    @izi.cli()
    def test(value_1=None, value_2=None):
        return 'Hi!'

    assert izi.test.cli(test) == 'Hi!'


def test_cli_with_exception():
    """Test to ensure that a cli with an exception is correctly handled"""
    @izi.cli()
    def test():
        raise ValueError()
        return 'Hi!'

    assert izi.test.cli(test) != 'Hi!'


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_wraps():
    """Test to ensure you can safely apply decorators to izi endpoints by using @izi.wraps"""
    def my_decorator(function):
        @izi.wraps(function)
        def decorated(*args, **kwargs):
            kwargs['name'] = 'Timothy'
            return function(*args, **kwargs)
        return decorated

    @izi.get()
    @my_decorator
    def what_is_my_name(izi_timer=None, name="Sam"):
        return {'name': name, 'took': izi_timer}

    result = izi.test.get(api, 'what_is_my_name').data
    assert result['name'] == 'Timothy'
    assert result['took']

    def my_second_decorator(function):
        @izi.wraps(function)
        def decorated(*args, **kwargs):
            kwargs['name'] = "Not telling"
            return function(*args, **kwargs)
        return decorated

    @izi.get()
    @my_decorator
    @my_second_decorator
    def what_is_my_name2(izi_timer=None, name="Sam"):
        return {'name': name, 'took': izi_timer}

    result = izi.test.get(api, 'what_is_my_name2').data
    assert result['name'] == "Not telling"
    assert result['took']

    def my_decorator_with_request(function):
        @izi.wraps(function)
        def decorated(request, *args, **kwargs):
            kwargs['has_request'] = bool(request)
            return function(*args, **kwargs)
        return decorated

    @izi.get()
    @my_decorator_with_request
    def do_you_have_request(has_request=False):
        return has_request

    assert izi.test.get(api, 'do_you_have_request').data


def test_cli_with_empty_return():
    """Test to ensure that if you return None no data will be added to sys.stdout"""
    @izi.cli()
    def test_empty_return():
        pass

    assert not izi.test.cli(test_empty_return)


def test_cli_with_multiple_ints():
    """Test to ensure multiple ints work with CLI"""
    @izi.cli()
    def test_multiple_cli(ints: izi.types.comma_separated_list):
        return ints

    assert izi.test.cli(test_multiple_cli, ints='1,2,3') == ['1', '2', '3']


    class ListOfInts(izi.types.Multiple):
        """Only accept a list of numbers."""

        def __call__(self, value):
            value = super().__call__(value)
            return [int(number) for number in value]

    @izi.cli()
    def test_multiple_cli(ints: ListOfInts()=[]):
        return ints

    assert izi.test.cli(test_multiple_cli, ints=['1', '2', '3']) == [1, 2, 3]

    @izi.cli()
    def test_multiple_cli(ints: izi.types.Multiple[int]()=[]):
        return ints

    assert izi.test.cli(test_multiple_cli, ints=['1', '2', '3']) == [1, 2, 3]


def test_startup():
    """Test to ensure izi startup decorators work as expected"""
    @izi.startup()
    def happens_on_startup(api):
        pass

    @izi.startup()
    @coroutine
    def async_happens_on_startup(api):
        pass

    assert happens_on_startup in api.startup_handlers
    assert async_happens_on_startup in api.startup_handlers


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_adding_headers():
    """Test to ensure it is possible to inject response headers based on only the URL route"""
    @izi.get(response_headers={'name': 'Timothy'})
    def endpoint():
        return ''

    result = izi.test.get(api, 'endpoint')
    assert result.data == ''
    assert result.headers_dict['name'] == 'Timothy'


def test_on_demand_404(izi_api):
    """Test to ensure it's possible to route to a 404 response on demand"""
    @izi_api.route.http.get()
    def my_endpoint(izi_api):
        return izi_api.http.not_found

    assert '404' in izi.test.get(izi_api, 'my_endpoint').status


    @izi_api.route.http.get()
    def my_endpoint2(izi_api):
        raise izi.HTTPNotFound()

    assert '404' in izi.test.get(izi_api, 'my_endpoint2').status

    @izi_api.route.http.get()
    def my_endpoint3(izi_api):
        """Test to ensure base 404 handler works as expected"""
        del izi_api.http._not_found
        return izi_api.http.not_found

    assert '404' in izi.test.get(izi_api, 'my_endpoint3').status


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_exceptions():
    """Test to ensure izi's exception handling decorator works as expected"""
    @izi.get()
    def endpoint():
        raise ValueError('hi')

    with pytest.raises(ValueError):
        izi.test.get(api, 'endpoint')

    @izi.exception()
    def handle_exception(exception):
        return 'it worked'

    assert izi.test.get(api, 'endpoint').data == 'it worked'

    @izi.exception(ValueError)  # noqa
    def handle_exception(exception):
        return 'more explicit handler also worked'

    assert izi.test.get(api, 'endpoint').data == 'more explicit handler also worked'


@pytest.mark.skipif(sys.platform == 'win32', reason='Currently failing on Windows build')
def test_validate():
    """Test to ensure izi's secondary validation mechanism works as expected"""
    def contains_either(fields):
        if not 'one' in fields and not 'two' in fields:
            return {'one': 'must be defined', 'two': 'must be defined'}

    @izi.get(validate=contains_either)
    def my_endpoint(one=None, two=None):
        return True


    assert izi.test.get(api, 'my_endpoint', one=True).data
    assert izi.test.get(api, 'my_endpoint', two=True).data
    assert izi.test.get(api, 'my_endpoint').status
    assert izi.test.get(api, 'my_endpoint').data == {'errors': {'one': 'must be defined', 'two': 'must be defined'}}


def test_cli_api(capsys):
    """Ensure that the overall CLI Interface API works as expected"""
    @izi.cli()
    def my_cli_command():
        print("Success!")

    with mock.patch('sys.argv', ['/bin/command', 'my_cli_command']):
        __izi__.cli()
        out, err = capsys.readouterr()
        assert "Success!" in out

    with mock.patch('sys.argv', []):
        with pytest.raises(SystemExit):
            __izi__.cli()


def test_cli_api_return():
    """Ensure returning from a CLI API works as expected"""
    @izi.cli()
    def my_cli_command():
        return "Success!"

    my_cli_command.interface.cli()


def test_urlencoded():
    """Ensure that urlencoded input format works as intended"""
    @izi.post()
    def test_url_encoded_post(**kwargs):
        return kwargs

    test_data = b'foo=baz&foo=bar&name=John+Doe'
    assert izi.test.post(api, 'test_url_encoded_post', body=test_data, headers={'content-type': 'application/x-www-form-urlencoded'}).data == {'name': 'John Doe', 'foo': ['baz', 'bar']}


def test_multipart():
    """Ensure that multipart input format works as intended"""
    @izi.post()
    def test_multipart_post(**kwargs):
        return kwargs

    with open(os.path.join(BASE_DIRECTORY, 'artwork', 'logo.png'),'rb') as logo:
        prepared_request = requests.Request('POST', 'http://localhost/', files={'logo': logo}).prepare()
        logo.seek(0)
        output = json.loads(izi.defaults.output_format({'logo': logo.read()}).decode('utf8'))
        assert izi.test.post(api, 'test_multipart_post',  body=prepared_request.body,
                             headers=prepared_request.headers).data == output


def test_json_null(izi_api):
    """Test to ensure passing in null within JSON will be seen as None and not allowed by text values"""
    @izi_api.route.http.post()
    def test_naive(argument_1):
        return argument_1

    assert izi.test.post(izi_api, 'test_naive', body='{"argument_1": null}',
                         headers={'content-type': 'application/json'}).data == None


    @izi_api.route.http.post()
    def test_text_type(argument_1: izi.types.text):
        return argument_1


    assert 'errors' in izi.test.post(izi_api, 'test_text_type', body='{"argument_1": null}',
                                    headers={'content-type': 'application/json'}).data


def test_json_self_key(izi_api):
    """Test to ensure passing in a json with a key named 'self' works as expected"""
    @izi_api.route.http.post()
    def test_self_post(body):
        return body

    assert izi.test.post(izi_api, 'test_self_post', body='{"self": "this"}',
                         headers={'content-type': 'application/json'}).data == {"self": "this"}


def test_204_with_no_body(izi_api):
    """Test to ensure returning no body on a 204 statused endpoint works without issue"""
    @izi_api.route.http.delete()
    def test_route(response):
        response.status = izi.HTTP_204
        return

    assert '204' in izi.test.delete(izi_api, 'test_route').status


def test_output_format_inclusion(izi_api):
    """Test to ensure output format can live in one api but apply to the other"""
    @izi.get()
    def my_endpoint():
        return 'hello'

    @izi.default_output_format(api=izi_api)
    def mutated_json(data):
        return izi.output_format.json({'mutated': data})

    izi_api.extend(api, '')

    assert izi.test.get(izi_api, 'my_endpoint').data == {'mutated': 'hello'}


def test_api_pass_along(izi_api):
    """Test to ensure the correct API instance is passed along using API directive"""
    @izi.get()
    def takes_api(izi_api):
        return izi_api.__name__

    izi_api.__name__ = "Test API"
    izi_api.extend(api, '')
    assert izi.test.get(izi_api, 'takes_api').data == izi_api.__name__


def test_exception_excludes(izi_api):
    """Test to ensure it's possible to add excludes to exception routers"""
    class MyValueError(ValueError):
        pass

    class MySecondValueError(ValueError):
        pass

    @izi.exception(Exception, exclude=MySecondValueError, api=izi_api)
    def base_exception_handler(exception):
        return 'base exception handler'

    @izi.exception(ValueError, exclude=(MyValueError, MySecondValueError), api=izi_api)
    def base_exception_handler(exception):
        return 'special exception handler'

    @izi.get(api=izi_api)
    def my_handler():
        raise MyValueError()

    @izi.get(api=izi_api)
    def fall_through_handler():
        raise ValueError('reason')

    @izi.get(api=izi_api)
    def full_through_to_raise():
        raise MySecondValueError()

    assert izi.test.get(izi_api, 'my_handler').data == 'base exception handler'
    assert izi.test.get(izi_api, 'fall_through_handler').data == 'special exception handler'
    with pytest.raises(MySecondValueError):
        assert izi.test.get(izi_api, 'full_through_to_raise').data


def test_cli_kwargs(izi_api):
    """Test to ensure cli commands can correctly handle **kwargs"""
    @izi.cli(api=izi_api)
    def takes_all_the_things(required_argument, named_argument=False, *args, **kwargs):
        return [required_argument, named_argument, args, kwargs]

    assert izi.test.cli(takes_all_the_things, 'hi!') == ['hi!', False, (), {}]
    assert izi.test.cli(takes_all_the_things, 'hi!', named_argument='there') == ['hi!', 'there', (), {}]
    assert izi.test.cli(takes_all_the_things, 'hi!', 'extra', '--arguments', 'can', '--happen', '--all', 'the', 'tim') \
                             == ['hi!', False, ('extra', ), {'arguments': 'can', 'happen': True, 'all': ['the', 'tim']}]


def test_api_gets_extra_variables_without_kargs_or_kwargs(izi_api):
    """Test to ensure it's possiible to extra all params without specifying them exactly"""
    @izi.get(api=izi_api)
    def ensure_params(request, response):
        return request.params

    assert izi.test.get(izi_api, 'ensure_params', params={'make': 'it'}).data == {'make': 'it'}
    assert izi.test.get(izi_api, 'ensure_params', hello='world').data == {'hello': 'world'}


def test_utf8_output(izi_api):
    """Test to ensure unicode data is correct outputed on JSON outputs without modification"""
    @izi.get(api=izi_api)
    def output_unicode():
        return {'data': 'Τη γλώσσα μου έδωσαν ελληνική'}

    assert izi.test.get(izi_api, 'output_unicode').data == {'data': 'Τη γλώσσα μου έδωσαν ελληνική'}


def test_param_rerouting(izi_api):
    @izi.local(api=izi_api, map_params={'local_id': 'record_id'})
    @izi.cli(api=izi_api, map_params={'cli_id': 'record_id'})
    @izi.get(api=izi_api, map_params={'id': 'record_id'})
    def pull_record(record_id: izi.types.number):
        return record_id

    assert izi.test.get(izi_api, 'pull_record', id=10).data == 10
    assert izi.test.get(izi_api, 'pull_record', id='10').data == 10
    assert 'errors' in izi.test.get(izi_api, 'pull_record', id='ten').data
    assert izi.test.cli(pull_record, cli_id=10) == 10
    assert izi.test.cli(pull_record, cli_id='10') == 10
    with pytest.raises(SystemExit):
        izi.test.cli(pull_record, cli_id='ten')
    assert pull_record(local_id=10)

    @izi.get(api=izi_api, map_params={'id': 'record_id'})
    def pull_record(record_id: izi.types.number=1):
        return record_id

    assert izi.test.get(izi_api, 'pull_record').data == 1
    assert izi.test.get(izi_api, 'pull_record', id=10).data == 10
