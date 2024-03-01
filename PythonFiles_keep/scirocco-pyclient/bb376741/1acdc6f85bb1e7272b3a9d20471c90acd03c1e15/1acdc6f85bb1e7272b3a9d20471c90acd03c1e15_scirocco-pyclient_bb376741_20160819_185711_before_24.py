import unittest

from client.responses import ClientMessageResponse, ClientBatchResponse


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


class ClientBatchResponseTest(unittest.TestCase):
    def setUp(self):
        self.client_batch_response = ClientBatchResponse()

    def test_property_messages_data_exist(self):
        self.assertTrue(hasattr(self.client_batch_response, 'messages_data'))

    def test_property_messages_data_default_none(self):
        self.assertIsNone(self.client_batch_response.messages_data)

    def test_property_system_data_exist(self):
        self.assertTrue(hasattr(self.client_batch_response, 'system_data'))

    def test_property_system_data_default_none(self):
        self.assertIsNone(self.client_batch_response.system_data)
