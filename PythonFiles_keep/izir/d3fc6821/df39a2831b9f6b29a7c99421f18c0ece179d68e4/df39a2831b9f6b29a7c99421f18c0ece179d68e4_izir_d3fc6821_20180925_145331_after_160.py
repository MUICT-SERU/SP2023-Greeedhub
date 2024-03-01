"""tests/test_api.py.

Tests to ensure the API object that stores the state of each individual izi endpoint works as expected

Copyright (C) 2016 Timothy Edmund Crosley

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

import izi

api = izi.API(__name__)


class TestAPI(object):
    """A collection of tests to ensure the izi API object interacts as expected"""

    def test_singleton(self):
        """Test to ensure there can only be one izi API per module"""
        assert izi.API(__name__) == api

    def test_context(self):
        """Test to ensure the izi singleton provides a global modifiable context"""
        assert not hasattr(izi.API(__name__), '_context')
        assert izi.API(__name__).context == {}
        assert hasattr(izi.API(__name__), '_context')

    def test_dynamic(self):
        """Test to ensure it's possible to dynamically create new modules to house APIs based on name alone"""
        new_api = izi.API('module_created_on_the_fly')
        assert new_api.module.__name__ == 'module_created_on_the_fly'
        import module_created_on_the_fly
        assert module_created_on_the_fly
        assert module_created_on_the_fly.__izi__ == new_api


def test_from_object():
    """Test to ensure it's possible to rechieve an API singleton from an arbitrary object"""
    assert izi.api.from_object(TestAPI) == api


def test_api_fixture(izi_api):
    """Ensure it's possible to dynamically insert a new izi API on demand"""
    assert isinstance(izi_api, izi.API)
    assert izi_api != api


def test_anonymous():
    """Ensure it's possible to create anonymous APIs"""
    assert izi.API() != izi.API() != api
    assert izi.API().module == None
    assert izi.API().name == ''
    assert izi.API(name='my_name').name == 'my_name'
    assert izi.API(doc='Custom documentation').doc == 'Custom documentation'


def test_api_routes(izi_api):
    """Ensure http API can return a quick mapping all urls to method"""
    izi_api.http.base_url = '/root'

    @izi.get(api=izi_api)
    def my_route():
        pass

    @izi.post(api=izi_api)
    def my_second_route():
        pass

    @izi.cli(api=izi_api)
    def my_cli_command():
        pass

    assert list(izi_api.http.urls()) == ['/root/my_route', '/root/my_second_route']
    assert list(izi_api.http.handlers()) == [my_route.interface.http, my_second_route.interface.http]
    assert list(izi_api.handlers()) == [my_route.interface.http, my_second_route.interface.http,
                                        my_cli_command.interface.cli]


def test_cli_interface_api_with_exit_codes(izi_api_error_exit_codes_enabled):
    api = izi_api_error_exit_codes_enabled

    @izi.object(api=api)
    class TrueOrFalse:
        @izi.object.cli
        def true(self):
            return True

        @izi.object.cli
        def false(self):
            return False

    api.cli(args=[None, 'true'])

    with pytest.raises(SystemExit):
        api.cli(args=[None, 'false'])


def test_cli_interface_api_without_exit_codes():
    @izi.object(api=api)
    class TrueOrFalse:
        @izi.object.cli
        def true(self):
            return True

        @izi.object.cli
        def false(self):
            return False

    api.cli(args=[None, 'true'])
    api.cli(args=[None, 'false'])
