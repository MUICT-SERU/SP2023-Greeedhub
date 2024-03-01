import unittest

from urllib3._collections import HTTPHeaderDict
from urllib3.request import urlencode

from pyddsclient.httpdao.requestsadapter import RequestsAdapter, RequestResponse, RequestManagerResponseHandler, \
    DataTypeConverter
from test.mocks import RequestManagerMock, Bunch


class RequestsAdapterTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestsAdapter('https://dds.sandboxwebs.com', 'af123', 'tok', RequestManagerMock(),
                                               RequestManagerResponseHandler())

    def test_from_header_fixed_property(self):
        self.assertEquals('DDS-node-id', self.request_adapter.from_header)

    def test_node_id_mandatory_property(self):
        self.assertEquals('af123', self.request_adapter.node_id)

    def test_api_url_mandatory_property(self):
        self.assertEquals('tok', self.request_adapter.auth_token)

    def test_api_url_mandatory_propertie(self):
        self.assertEquals('https://dds.sandboxwebs.com', self.request_adapter.api_url)

    def test_get_uri(self):
        root = 'https://dds.sandboxwebs.com'
        self.assertEquals(root + '/resource', self.request_adapter.get_uri('/resource'))
        self.assertEquals(root + '/resource/subresource', self.request_adapter.get_uri('/resource/subresource/'))

    def test_get_headers_fixed_auth_header(self):
        headers = self.request_adapter.get_fixed_headers()
        self.assertEquals('tok', headers['Authorization'])

    def test_get_headers_fixed_from_header(self):
        headers = self.request_adapter.get_fixed_headers()
        self.assertEquals('af123', headers['DDS-node-id'])

    def test_get_headers_fixed_content_type_header(self):
        headers = self.request_adapter.get_fixed_headers()
        self.assertEquals('application/json', headers['Content-Type'])

    def test_request_added_headers_are_present_in_request(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}

        res = self.request_adapter.request('GET', data=data_fixture, headers=headers_fixture)
        self.assertEquals(res.http_headers.get('headerExtra'), 'extraextra!')

    def test_request_method_in_request_is_uppercased(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('get', data=data_fixture, headers=headers_fixture)
        self.assertEquals('GET', res.message_data['method'])

    def test_request_get_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('GET', '/resource', data_fixture)
        self.assertEquals(res.message_data['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_request_delete_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('DELETE', '/resource', data_fixture)
        self.assertEquals(res.message_data['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_request_post_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('POST', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_request_put_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('PUT', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_request_patch_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('PATCH', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])


class RequestManagerResponseHandlerTest(unittest.TestCase):
    def setUp(self):
        self.rarh = RequestManagerResponseHandler()

    def test_handle_response_is_a_request_response_object(self):
        response_fixture = Bunch(headers={"asda": "asda"},
                                 status=200,
                                 data={"to_node_id": "af123", "data": {"number": 342}})
        res = self.rarh.handle(response_fixture)

        self.assertIsInstance(res, RequestResponse)

    def test_handle_message_data_is_isolated_from_system_data(self):
        response_fixture = Bunch(headers={"asda": "asda"},
                                 status=200,
                                 data={"to_node_id": "af123", "data": {"number": 342}})

        res = self.rarh.handle(response_fixture)
        self.assertIsInstance(res, RequestResponse)
        self.assertDictEqual(res.system_data, {"to_node_id": "af123"})
        self.assertDictEqual(res.message_data, {"number": 342})


class RequestResponseTest(unittest.TestCase):
    def setUp(self):
        self.cli_resp = RequestResponse()

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
        self.assertEquals(data, self.cli_resp.http_status)


class DataTypeConverterTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_all_to_obj_received_object_left_intact(self):
        data_object = {"field1": "value1", "field2": "value2"}
        res = DataTypeConverter.all_to_obj(data_object.copy())
        self.assertDictEqual(res, data_object.copy())

    def test_all_to_obj_received_json_is_converted_to_dict(self):
        strstr = '{"field1": "value1", "field2": "value2"}'
        res = DataTypeConverter.all_to_obj(strstr)
        self.assertDictEqual(res, {"field1": "value1", "field2": "value2"})

    def test_all_to_obj_received_bytes_is_converted_to_dict(self):
        btes = '{"field1": "value1", "field2": "value2"}'.encode("utf8")
        res = DataTypeConverter.all_to_obj(btes)
        self.assertDictEqual(res, {"field1": "value1", "field2": "value2"})

    def test_all_to_obj_received_http_header_dict_left_intact(self):
        header_dict = HTTPHeaderDict()
        header_dict.add("auth", "auth")
        header_dict.add("test", "test")

        res_header_dict = DataTypeConverter.all_to_obj(header_dict)
        self.assertIsInstance(res_header_dict, HTTPHeaderDict)

    def test_all_to_obj_received_empty_bytes_is_converted_to_none(self):
        btes_empty = ''.encode("utf8")
        no_json_parseable = DataTypeConverter.all_to_obj(btes_empty)
        self.assertIsNone(no_json_parseable)

    def test_all_to_obj_received_empty_str_is_converted_to_none(self):
        str_empty = ''
        no_json_parseable = DataTypeConverter.all_to_obj(str_empty)
        self.assertIsNone(no_json_parseable)

    def test_all_to_obj_received_list_object_left_intact(self):
        array_list = [{"item1": "value1"}]
        res = DataTypeConverter.all_to_obj(array_list.copy())
        self.assertListEqual(res, array_list.copy())

    def dummy_function(self):
        pass

    def test_all_to_obj_received_unknown_raises_exception(self):
        with self.assertRaises(TypeError):
            DataTypeConverter.all_to_obj(self.dummy_function)

    def test_all_to_int_received_int_left_intact(self):
        integer = 22
        res = DataTypeConverter.all_to_int(integer)
        self.assertEquals(22, res)

    def test_all_to_int_received_str_is_converted_to_int(self):
        integer = '22'
        res = DataTypeConverter.all_to_int(integer)
        self.assertEquals(22, res)

    def test_all_to_int_received_bytes_is_converted_to_int(self):
        btes = '22'.encode("utf8")
        res = DataTypeConverter.all_to_int(btes)
        self.assertEquals(22, res)

    def test_all_to_int_received_unknown_raises_exception(self):
        dicttio = {"field1": "value1", "field2": "value2"}
        with self.assertRaises(TypeError):
            DataTypeConverter.all_to_int(dicttio)
