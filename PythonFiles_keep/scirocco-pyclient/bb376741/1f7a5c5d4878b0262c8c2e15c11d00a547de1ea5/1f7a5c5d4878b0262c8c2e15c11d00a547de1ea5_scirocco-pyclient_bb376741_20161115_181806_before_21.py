import unittest

from sciroccoclient.responses import ClientMessageResponse


class ClientMessageResponseTest(unittest.TestCase):
    def setUp(self):
        self.client_message_response = ClientMessageResponse()

    def test_property_message_data_exist(self):
        self.assertTrue(hasattr(self.client_message_response, 'message_data'))

    def test_property_message_data_default_none(self):
        self.assertIsNone(self.client_message_response.message_data)

    def test_property_system_data_exist(self):
        self.assertTrue(hasattr(self.client_message_response, 'system_data'))

    def test_property_system_data_default_none(self):
        self.assertIsNone(self.client_message_response.system_data)