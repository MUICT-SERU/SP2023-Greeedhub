import base64
import os
import unittest

from sciroccoclient.httpclient import HTTPClient


class MessagesGetOneInterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = HTTPClient('http://localhost', 'af123', 'DEFAULT_TOKEN')
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            cls.binary_fixture = f.read()

    def setUp(self):
        self.client.message_delete_all()

    def test_get_one_with_string_payload(self):
        message = 'message'
        response_push = self.client.message_queue_push('af123', message)
        response_message_get = self.client.message_get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, message)
        self.assertEqual(response_message_get.system_data.data_type, 'text/plain')

    def test_get_one_with_object_payload(self):
        message = {"name": "message", "type": "object"}
        response_push = self.client.message_queue_push('af123', message)
        response_message_get = self.client.message_get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, message)
        self.assertEqual(response_message_get.system_data.data_type, 'application/json')

    def test_get_one_with_binary_payload(self):
        message = self.binary_fixture
        response_push = self.client.message_queue_push('af123', message)
        response_message_get = self.client.message_get(response_push.system_data.id)
        self.assertEqual(base64.b64decode(response_message_get.message_data), message)
        self.assertEqual(response_message_get.system_data.data_type, 'application/octet-stream')

    def test_get_one_do_not_alter_anything_in_message(self):
        message = 'message'
        response_push = self.client.message_queue_push('af123', message)
        response_message_get = self.client.message_get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, response_message_get.message_data)
        self.assertEqual(str(sorted(response_push.system_data.__dict__)),
                         str(sorted(response_message_get.system_data.__dict__)))


class MessageGetAllInterfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = HTTPClient('http://localhost', 'af123', 'DEFAULT_TOKEN')
        with open(os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'tux.pdf'), 'rb') as f:
            cls.binary_fixture = f.read()

    def setUp(self):
        self.client.message_delete_all()

    def test_get_all_brings_all_pending_messages(self):
        for m in range(10):
            self.client.message_queue_push('af123', 'This is message ' + str(m))
        response = self.client.message_get_all()
        asda = "sdsd"
