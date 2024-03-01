import unittest

from pyddsclient.httpdao.requestresponse import RequestResponse


class RequestResponseTest(unittest.TestCase):

    def setUp(self):
        self.cli_resp = RequestResponse()

    def test_members_initial_none(self):

        self.assertIsNone(self.cli_resp.system_data)
        self.assertIsNone(self.cli_resp.message_data)

    def test_data_input_str_may_be_converted_to_object(self):

        str = '{"field1": "value1", "field2": "value2"}'
        self.cli_resp.message_data = str
        self.cli_resp.system_data = str

        self.assertIsInstance(self.cli_resp.message_data, dict)
        self.assertIsInstance(self.cli_resp.system_data, dict)

    def test_data_input_bytes_may_be_converted_to_object(self):

        btes = '{"field1": "value1", "field2": "value2"}'.encode("utf8")

        self.cli_resp.message_data = btes
        self.cli_resp.system_data = btes

        self.assertIsInstance(self.cli_resp.message_data, dict)
        self.assertIsInstance(self.cli_resp.system_data, dict)

    def test_data_input_object_may_be_not_converted(self):

        data_object = {"field1": "value1", "field2": "value2"}

        self.cli_resp.message_data = data_object
        self.cli_resp.system_data = data_object

        self.assertIsInstance(self.cli_resp.message_data, dict)
        self.assertIsInstance(self.cli_resp.system_data, dict)



