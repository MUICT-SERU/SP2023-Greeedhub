import copy
import json
import os
import unittest

from urllib3.request import urlencode

from sciroccoclient.exceptions import SciroccoInitParamsError
from sciroccoclient.http.requestadapter import RequestsAdapter, RequestAdapterResponse, RequestManagerResponseHandler, \
    RequestAdapterDataResponseHandler, RequestAdapterContentTypeDetector
from sciroccoclient.systemdata import SystemDataDescriptor, SystemData, SystemDataHTTPHeadersFilter, \
    SystemDataHydrator
from test.unit.mocks import RequestManagerMock, Bunch


class RequestsAdapterTest(unittest.TestCase):
    def setUp(self):
        system_data_http_headers_filter = SystemDataHTTPHeadersFilter(SystemDataDescriptor(SystemData()))

        self.request_adapter = RequestsAdapter(RequestManagerMock(),
                                               RequestManagerResponseHandler(system_data_http_headers_filter,
                                                                             SystemDataHydrator(),
                                                                             RequestAdapterDataResponseHandler()),
                                               SystemDataDescriptor(SystemData()),
                                               RequestAdapterContentTypeDetector())

        self.request_adapter_without_runtime = copy.deepcopy(self.request_adapter)
        self.request_adapter.api_url = 'https://dds.sandboxwebs.com'
        self.request_adapter.node_id = 'af123'
        self.request_adapter.auth_token = 'tok'

    def test_from_header_fixed_property(self):
        self.assertEqual('Scirocco-From', self.request_adapter.system_data_http.get_http_header_by_field_name('fromm'))

    def test_node_id_mandatory_property(self):
        self.assertEqual('af123', self.request_adapter.node_id)

    def test_api_token_mandatory_property(self):
        self.assertEqual('tok', self.request_adapter.auth_token)

    def test_api_url_mandatory_property(self):
        self.assertEqual('https://dds.sandboxwebs.com', self.request_adapter.api_url)

    def test_property_api_url_exits(self):
        self.assertTrue(hasattr(self.request_adapter, "api_url"))

    def test_property_node_id_exits(self):
        self.assertTrue(hasattr(self.request_adapter, "node_id"))

    def test_property_auth_token_exits(self):
        self.assertTrue(hasattr(self.request_adapter, "auth_token"))

    def test_runtime_properties_are_unsetted(self):
        self.assertIsNone(self.request_adapter_without_runtime.api_url)
        self.assertIsNone(self.request_adapter_without_runtime.node_id)
        self.assertIsNone(self.request_adapter_without_runtime.auth_token)

    def test_exec_without_runtime_node_id_fails(self):
        self.request_adapter_without_runtime.api_url = 'url'
        self.request_adapter_without_runtime.auth_token = '45345'
        self.assertRaises(SciroccoInitParamsError, self.request_adapter_without_runtime.request, 'GET', '/resource')

    def test_exec_without_runtime_api_url_fails(self):
        self.request_adapter_without_runtime.auth_token = '45345'
        self.request_adapter_without_runtime.node_id = '45345'
        self.assertRaises(SciroccoInitParamsError, self.request_adapter_without_runtime.request, 'GET', '/resource')

    def test_exec_without_runtime_auth_token_fails(self):
        self.request_adapter_without_runtime.api_url = 'url'
        self.request_adapter_without_runtime.node_id = '45345'
        self.assertRaises(SciroccoInitParamsError, self.request_adapter_without_runtime.request, 'GET', '/resource')

    def test_get_uri(self):
        root = 'https://dds.sandboxwebs.com'
        self.assertEqual(root + '/resource', self.request_adapter.get_uri('/resource'))
        self.assertEqual(root + '/resource/subresource', self.request_adapter.get_uri('/resource/subresource/'))

    def test_get_headers_fixed_auth_header(self):
        headers = self.request_adapter.get_fixed_headers()
        self.assertEqual('tok', headers['Authorization'])

    def test_get_headers_fixed_from_header(self):
        headers = self.request_adapter.get_fixed_headers()
        self.assertEqual('af123', headers['Scirocco-From'])

    def test_request_added_headers_are_present_in_request(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}

        res = self.request_adapter.request('GET', data=data_fixture, headers=headers_fixture)
        self.assertEqual(res.http_headers['headerExtra'], 'extraextra!')

    def test_request_method_in_request_is_uppercased(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('get', data=data_fixture, headers=headers_fixture)
        self.assertEqual('GET', res.http_headers['method'])

    def test_request_get_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('GET', '/resource', data_fixture)
        self.assertEqual(res.http_headers['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_request_delete_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('DELETE', '/resource', data_fixture)
        self.assertEqual(res.http_headers['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_request_post_method_data_is_same_as_body(self):
        data_fixture = {"name": "eloy", "test": True}

        res = self.request_adapter.request('POST', '/resource', data_fixture.copy())
        self.assertEqual(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_request_put_method_data_is_same_as_body(self):
        data_fixture = {"name": "eloy", "test": True}

        res = self.request_adapter.request('PUT', '/resource', data_fixture)
        self.assertEqual(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_request_patch_method_data_is_same_as_body(self):
        data_fixture = {"name": "eloy", "test": True}

        res = self.request_adapter.request('PATCH', '/resource', data_fixture)
        self.assertEqual(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])


class RequestManagerResponseHandlerTest(unittest.TestCase):
    def setUp(self):
        self.system_data_headers_descriptor = SystemDataDescriptor(SystemData())
        system_data_http_headers_filter = SystemDataHTTPHeadersFilter(self.system_data_headers_descriptor)
        system_data_hydrator = SystemDataHydrator()
        data_treatment = RequestAdapterDataResponseHandler()
        self.response_handler = RequestManagerResponseHandler(system_data_http_headers_filter, system_data_hydrator,
                                                              data_treatment)

    def test_method_handle_exists(self):
        self.assertTrue("handle" in dir(self.response_handler))

    def test_return_type_request_adapter_response(self):
        response = Bunch(
            headers={
                self.system_data_headers_descriptor.get_http_header_by_field_name('fromm'): "af123",
                "Cookie": "adasdsa"
            },
            data="asdaasdaasd".encode(),
            status=201
        )
        res = self.response_handler.handle(response)

        self.assertIsInstance(res, RequestAdapterResponse)

class RequestAdapterDataResponseHandlerTest(unittest.TestCase):
    def setUp(self):
        self.data_treat = RequestAdapterDataResponseHandler()

    def test_method_treat_data_exists(self):
        self.assertTrue("treat" in dir(self.data_treat))

    def test_treat_data_converts_json(self):
        data = '{"name": "test"}'.encode()
        res = self.data_treat.treat(data)
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, json.loads(data.decode()))

    def test_treat_data_plain_text_accept(self):
        data = 'string'.encode()
        res = self.data_treat.treat(data)
        self.assertIsInstance(res, str)
        self.assertEqual(res, data.decode())

    def test_treat_data_binary(self):
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            data = f.read()
        res = self.data_treat.treat(data)
        self.assertIsInstance(res, bytes)


class RequestAdapterContentTypeDetectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            cls.bin_fixture = f.read()

    def setUp(self):
        self.req_adapter_content_type = RequestAdapterContentTypeDetector()

    def test_detect_from_body_exists(self):
        self.assertTrue("detect_from_body" in dir(self.req_adapter_content_type))

    def test_check_for_string_exists(self):
        self.assertTrue("check_for_string" in dir(self.req_adapter_content_type))

    def test_check_for_object_exists(self):
        self.assertTrue("check_for_object" in dir(self.req_adapter_content_type))

    def test_check_for_binary_exists(self):
        self.assertTrue("check_for_binary" in dir(self.req_adapter_content_type))

    def test_detect_from_body_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.req_adapter_content_type.detect_from_body, "sdsd", "sdsd")

    def test_check_for_string_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.req_adapter_content_type.detect_from_body, "sdsd", "sdsd")

    def test_check_for_object_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.req_adapter_content_type.detect_from_body, "sdsd", "sdsd")

    def test_check_for_binary_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.req_adapter_content_type.detect_from_body, "sdsd", "sdsd")

    def test_detect_from_body_since_body_is_binary(self):
        res = self.req_adapter_content_type.detect_from_body(self.bin_fixture)

        self.assertEqual(res, 'application/octet-stream')

    def test_detect_from_body_since_body_is_object(self):
        body = {"name": "body", "type": "json object"}

        res = self.req_adapter_content_type.detect_from_body(body)

        self.assertEqual(res, 'application/json')

    def test_detect_from_body_since_body_is_string(self):
        body = "this is a body string."

        res = self.req_adapter_content_type.detect_from_body(body)

        self.assertEqual(res, 'text/plain')

    def test_check_for_string(self):
        fixture = "stringggggggggggggg"

        res = self.req_adapter_content_type.check_for_string(fixture)
        self.assertTrue(res)

        fixture = {}
        res = self.req_adapter_content_type.check_for_string(fixture)
        self.assertFalse(res)

        res = self.req_adapter_content_type.check_for_string(self.bin_fixture)
        self.assertFalse(res)

    def test_check_for_object(self):
        fixture = "stringggggggggggggg"

        res = self.req_adapter_content_type.check_for_object(fixture)
        self.assertFalse(res)

        fixture = {"name": "test"}
        res = self.req_adapter_content_type.check_for_object(fixture)
        self.assertTrue(res)

        fixture = '{"name": "test"}'
        res = self.req_adapter_content_type.check_for_object(fixture)
        self.assertTrue(res)

        res = self.req_adapter_content_type.check_for_object(self.bin_fixture)
        self.assertFalse(res)

    def test_check_for_bin(self):
        fixture = "stringggggggggggggg"

        res = self.req_adapter_content_type.check_for_binary(fixture)
        self.assertFalse(res)

        fixture = {}
        res = self.req_adapter_content_type.check_for_binary(fixture)
        self.assertFalse(res)

        res = self.req_adapter_content_type.check_for_binary(self.bin_fixture)
        self.assertTrue(res)


class RequestResponseTest(unittest.TestCase):
    def setUp(self):
        self.cli_resp = RequestAdapterResponse()

    def test_attribute_http_headers_exist(self):
        self.assertTrue(hasattr(self.cli_resp, 'http_headers'))

    def test_attribute_http_status_exist(self):
        self.assertTrue(hasattr(self.cli_resp, 'http_status'))

    def test_attribute_system_data_exist(self):
        self.assertTrue(hasattr(self.cli_resp, 'system_data'))

    def test_attribute_message_data_exist(self):
        self.assertTrue(hasattr(self.cli_resp, 'message_data'))

    def test_attribute_system_data_initial_value_is_none(self):
        self.assertIsNone(self.cli_resp.system_data)

    def test_attribute_message_data_initial_value_is_none(self):
        self.assertIsNone(self.cli_resp.message_data)

    def test_attribute_http_headers_initial_value_is_none(self):
        self.assertIsNone(self.cli_resp.http_headers)

    def test_attribute_http_status_initial_value_is_none(self):
        self.assertIsNone(self.cli_resp.http_status)

    def test_setter_message_data_not_modifies_output(self):
        data = {"field1": "value1", "field2": "value2"}
        self.cli_resp.message_data = data

        self.assertDictEqual(data, self.cli_resp.message_data)

    def test_setter_system_data_not_modifies_output(self):
        data = {"field1": "value1", "field2": "value2"}
        self.cli_resp.system_data = data

        self.assertDictEqual(data, self.cli_resp.system_data)

    def test_setter_http_headers_not_modifies_output(self):
        data = {"field1": "value1", "field2": "value2"}

        self.cli_resp.http_headers = data
        self.assertDictEqual(data, self.cli_resp.http_headers)

    def test_setter_http_status_not_modifies_output(self):
        data = 201
        self.cli_resp.http_status = data
        self.assertEqual(data, self.cli_resp.http_status)
