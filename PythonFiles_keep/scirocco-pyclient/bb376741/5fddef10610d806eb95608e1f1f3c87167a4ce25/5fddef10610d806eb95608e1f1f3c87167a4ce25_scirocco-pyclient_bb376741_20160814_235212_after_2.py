import unittest

from urllib3._collections import HTTPHeaderDict
from urllib3.request import urlencode

import pyddsclient.httpdao.requestsadapter
from test.mocks import RequestManagerMock, Bunch


class RequestsAdapterTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = pyddsclient.httpdao.requestsadapter.RequestsAdapter('af123', 'tok', RequestManagerMock(), pyddsclient.httpdao.requestsadapter.RequestManagerResponseHandler())

    def test_properties(self):
        self.assertEquals('https://dds.sandboxwebs.com', self.request_adapter.api_url)
        self.assertEquals('DDS-node-id', self.request_adapter.from_header)

    def test_mandatory_properties(self):
        self.assertEquals('af123', self.request_adapter.node_id)
        self.assertEquals('tok', self.request_adapter.auth_token)

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
        self.rarh = pyddsclient.httpdao.requestsadapter.RequestManagerResponseHandler()

    def test_handle(self):
        response_fixture = Bunch(headers={"asda": "asda"},
                                 status=200,
                                 data={"to_node_id": "af123", "data": {"number": 342}})
        res = self.rarh.handle(response_fixture)
        self.assertIsInstance(res, pyddsclient.httpdao.requestsadapter.RequestResponse)
        self.assertDictEqual(res.system_data, {"to_node_id": "af123"})
        self.assertDictEqual(res.message_data, {"number": 342})


class RequestResponseTest(unittest.TestCase):


    def setUp(self):
        self.cli_resp = pyddsclient.httpdao.requestsadapter.RequestResponse(pyddsclient.httpdao.requestsadapter.DataTypeConverter())

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
        data = "201"
        self.cli_resp.http_status = data
        self.assertEquals(int(data), self.cli_resp.http_status)

        with self.assertRaises(ValueError):
            data = "sdsd"
            self.cli_resp.http_status = data



class DataTypeConverterTest(unittest.TestCase):
    def setUp(self):
        self.converter = pyddsclient.httpdao.requestsadapter.DataTypeConverter()

    def test_data_converter(self):
        str = '{"field1": "value1", "field2": "value2"}'
        btes = '{"field1": "value1", "field2": "value2"}'.encode("utf8")
        data_object = {"field1": "value1", "field2": "value2"}
        header_dict = HTTPHeaderDict(field="val1", field2="val2")

        res1 = self.converter.all_to_dict(str)
        res2 = self.converter.all_to_dict(btes)
        res3 = self.converter.all_to_dict(data_object)
        res4 = self.converter.all_to_dict(header_dict)

        for r in [res1, res2, res3, res4]:
            self.assertIsInstance(r, dict)
