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

    def test_check_fixed_auth_header(self):
        headers = self.request_adapter.get_headers()
        self.assertEquals('tok', headers['Authorization'])

    def test_check_fixed_from_header(self):
        headers = self.request_adapter.get_headers()
        self.assertEquals('af123', headers['DDS-node-id'])

    def test_check_fixed_content_type_header(self):
        headers = self.request_adapter.get_headers()
        self.assertEquals('application/json', headers['Content-Type'])

    def test_check_that_added_headers_are_present_in_request(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}

        res = self.request_adapter.request('GET', data=data_fixture, headers=headers_fixture)
        self.assertEquals(res.http_headers.get('headerExtra'), 'extraextra!')

    def test_that_request_method_is_uppercased(self):
        headers_fixture = {"headerExtra": "extraextra!"}
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('get', data=data_fixture, headers=headers_fixture)
        self.assertEquals('GET', res.message_data['method'])

    def test_check_that_get_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('GET', '/resource', data_fixture)
        self.assertEquals(res.message_data['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_check_that_delete_method_data_is_same_as_url_params(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        res = self.request_adapter.request('DELETE', '/resource', data_fixture)
        self.assertEquals(res.message_data['url'],
                          ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data_fixture)]))

    def test_check_that_post_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('POST', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_check_that_put_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('PUT', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])

    def test_check_that_patch_method_data_is_same_as_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}

        res = self.request_adapter.request('PATCH', '/resource', data_fixture)
        self.assertEquals(res.message_data['name'], 'eloy')
        self.assertTrue(res.message_data['test'])


class RequestManagerResponseHandlerTest(unittest.TestCase):
    def setUp(self):
        self.rarh = RequestManagerResponseHandler()

    def test_handle(self):
        response_fixture = Bunch(headers={"asda": "asda"},
                                 status=200,
                                 data={"to_node_id": "af123", "data": {"number": 342}})

        res = self.rarh.handle(response_fixture)
        self.assertIsInstance(res, RequestResponse)
        self.assertDictEqual(res.system_data, {"to_node_id": "af123"})
        self.assertDictEqual(res.message_data, {"number": 342})

        fixture_empty_body = Bunch(headers={"asda": "asda"},
                                   status=200,
                                   data=''.encode("utf8"))
        res = self.rarh.handle(fixture_empty_body)

        self.assertEquals(res.system_data, None)
        self.assertEquals(res.message_data, None)


class RequestResponseTest(unittest.TestCase):
    def setUp(self):
        self.cli_resp = RequestResponse()

    def test_attributes_exist(self):
        self.assertTrue(hasattr(self.cli_resp, 'http_headers'))
        self.assertTrue(hasattr(self.cli_resp, 'http_status'))
        self.assertTrue(hasattr(self.cli_resp, 'system_data'))
        self.assertTrue(hasattr(self.cli_resp, 'system_data'))

    def test_members_initial_none(self):
        self.assertIsNone(self.cli_resp.system_data)
        self.assertIsNone(self.cli_resp.message_data)
        self.assertIsNone(self.cli_resp.http_headers)
        self.assertIsNone(self.cli_resp.http_status)

    def test_message_data(self):
        data = {"field1": "value1", "field2": "value2"}
        self.cli_resp.message_data = data

        self.assertDictEqual(data, self.cli_resp.message_data)

    def test_system_data(self):
        data = {"field1": "value1", "field2": "value2"}
        self.cli_resp.system_data = data

        self.assertDictEqual(data, self.cli_resp.system_data)

    def test_http_headers(self):
        data = {"field1": "value1", "field2": "value2"}

        self.cli_resp.http_headers = data
        self.assertDictEqual(data, self.cli_resp.http_headers)

    def test_http_status_code(self):
        data = 201
        self.cli_resp.http_status = data
        self.assertEquals(data, self.cli_resp.http_status)


class DataTypeConverterTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_data_converter_all_to_obj(self):
        str = '{"field1": "value1", "field2": "value2"}'
        btes = '{"field1": "value1", "field2": "value2"}'.encode("utf8")
        data_object = {"field1": "value1", "field2": "value2"}

        header_dict = HTTPHeaderDict()
        header_dict.add("auth", "auth")
        header_dict.add("test", "test")
        res_header_dict = DataTypeConverter.all_to_obj(header_dict)

        self.assertIsInstance(res_header_dict, HTTPHeaderDict)

        res1 = DataTypeConverter.all_to_obj(str)
        res2 = DataTypeConverter.all_to_obj(btes)
        res3 = DataTypeConverter.all_to_obj(data_object)

        for r in [res1, res2, res3]:
            self.assertIsInstance(r, dict)

        btes_empty = ''.encode("utf8")
        no_json_parseable = DataTypeConverter.all_to_obj(btes_empty)
        self.assertEquals(no_json_parseable, None)

        array_obj = [{"item1": "value1"}]
        res = DataTypeConverter.all_to_obj(array_obj)
        self.assertListEqual(res, array_obj)

    def test_data_converter_all_to_int(self):
        integer = 22
        str = '22'
        btes = '22'.encode("utf8")

        res1 = DataTypeConverter.all_to_int(str)
        res2 = DataTypeConverter.all_to_int(btes)
        res3 = DataTypeConverter.all_to_int(integer)

        for r in [res1, res2, res3]:
            self.assertEquals(22, r)

        dicttio = {"field1": "value1", "field2": "value2"}

        with self.assertRaises(TypeError):
            data = "sdsd"
            DataTypeConverter.all_to_int(dicttio)
