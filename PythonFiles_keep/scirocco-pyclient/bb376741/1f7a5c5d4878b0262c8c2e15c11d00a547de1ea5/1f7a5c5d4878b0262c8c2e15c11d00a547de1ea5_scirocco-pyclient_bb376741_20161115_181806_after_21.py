import unittest

from sciroccoclient.responses import ClientMessageResponse


class ClientMessageResponseTest(unittest.TestCase):
    def setUp(self):
        self.client_message_response = ClientMessageResponse()

    def test_property_payload_exist(self):
        self.assertTrue(hasattr(self.client_message_response, 'payload'))

    def test_property_payload_default_none(self):
        self.assertIsNone(self.client_message_response.payload)

    def test_property_metadata_exist(self):
        self.assertTrue(hasattr(self.client_message_response, 'metadata'))

    def test_property_metadata_default_none(self):
        self.assertIsNone(self.client_message_response.metadata)