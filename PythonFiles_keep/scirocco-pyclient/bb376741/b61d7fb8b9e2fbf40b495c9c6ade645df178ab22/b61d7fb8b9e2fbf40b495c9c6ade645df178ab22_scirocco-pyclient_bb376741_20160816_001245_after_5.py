import unittest

from urllib3._collections import HTTPHeaderDict
from urllib3.request import urlencode

from pyddsclient.httpdao.requestsadapter import RequestsAdapter, RequestResponse, RequestManagerResponseHandler, \
    DataTypeConverter
from test.mocks import RequestManagerMock, Bunch


class RequestsAdapterTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestsAdapter('https://dds.sandboxwebs.com', 'af123', 'tok', RequestManagerMock(), RequestManagerResponseHandler())

    def test_properties(self):
        self.assertEquals('DDS-node-id', self.request_adapter.from_header)

    def test_mandatory_properties(self):
        self.assertEquals('af123', self.request_adapter.node_id)
        self.assertEquals('tok', self.request_adapter.auth_token)
        self.assertEquals('https://dds.sandboxwebs.com', self.request_adapter.api_url)

    def test_get_url(self):
        root = 'https://dds.sandboxwebs.com'
        self.assertEquals(root + '/resource', self.request_adapter.get_url('/resource'))
        self.assertEquals(root + '/resource/subresource', self.request_adapter.get_url('/resource/subresource/'))

    def test_get_headers(self):
        headers = self.request_adapter.get_headers()
        self.assertEquals(headers['Authorization'], 'tok')
        self.assertEquals(headers['DDS-node-id'], 'af123')

    def test_request_methods_without_body(self):
        data_fixture = {"queryparam1": 23, "queryparam2": 34}
        headers_fixture = {"headerExtra": "extraextra!"}

        for m in ['get', 'delete']:
            data = data_fixture.copy()
            headers = headers_fixture.copy()

            res = self.request_adapter.request(m, '/resource', data, headers)
            self.assertEquals(4, len(res.http_headers))
            self.assertEquals('tok', res.http_headers['Authorization'])
            self.assertEquals('extraextra!', res.http_headers['headerExtra'])
            self.assertEquals('af123', res.http_headers['DDS-node-id'])
            self.assertEquals(res.message_data['method'], m.upper())
            self.assertIsInstance(res.message_data, dict)
            self.assertEquals(res.message_data['url'],
                              ''.join([self.request_adapter.api_url, '/resource', '?', urlencode(data)]))

    def test_request_methods_with_body(self):
        data_fixture = {"to_node_id": "af123", "data": {"name": "eloy", "test": True}}
        headers_fixture = {"headerExtra": "extraextra!"}

        for m in ['post', 'put', 'patch']:
            data = data_fixture.copy()
            headers = headers_fixture.copy()

            res = self.request_adapter.request(m, '/resource', data, headers)

            self.assertEquals(4, len(res.http_headers))
            self.assertEquals('tok', res.http_headers['Authorization'])
            self.assertEquals('extraextra!', res.http_headers['headerExtra'])
            self.assertEquals('af123', res.http_headers['DDS-node-id'])
            self.assertEquals(res.message_data['method'], m.upper())
            self.assertIsInstance(res.message_data, dict)
            self.assertEquals(res.message_data['url'], ''.join([self.request_adapter.api_url, '/resource']))

            del res.message_data['method']
            del res.message_data['url']
            self.assertDictEqual(res.message_data, data['data'])
            system_data = data
            del system_data['data']
            self.assertDictEqual(res.system_data, system_data)


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
