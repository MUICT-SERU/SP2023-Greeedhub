import base64
import os

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from test.integration.base import SciroccoTestBase


class MessageQueuePushInterfaceTest(SciroccoTestBase):
    def test_push_text_payload(self):
        message = 'This is my text message'
        response = self.client.message_queue_push('af123', message)
        self.assertEqual(response.message_data, message)
        self.assertEqual(response.system_data.data_type, 'text/plain')

    def test_push_object_payload(self):
        message = {"name": "message", "type": "object"}
        response = self.client.message_queue_push('af123', message)
        self.assertEqual(response.message_data, message)
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_push_binary_payload(self):
        message = self.binary_fixture
        response = self.client.message_queue_push('af123', message)
        self.assertEqual(message, response.message_data)
        self.assertEqual(response.system_data.data_type, 'application/octet-stream')

    def test_push_custom_data_type_is_respected(self):
        message = self.binary_fixture
        response = self.client.message_queue_push('af123', message, 'application/pdf')
        self.assertEqual(response.system_data.data_type, 'application/pdf')

    def test_push_too_much_data_raises_error(self):
        message = os.urandom(1550000)
        self.assertRaises(SciroccoHTTPDAOError, self.client.message_queue_push, 'af123', message)


class MessageQueuePullInterfaceTest(SciroccoTestBase):
    def test_pull_returns_none_if_no_messages_pending(self):
        response = self.client.message_queue_pull()
        self.assertIsNone(response)

    def test_pull_returns_type_string_when_sending_string(self):
        message = 'This is my string test.'
        self.client.message_queue_push('af123', message)
        response = self.client.message_queue_pull()
        self.assertEqual(response.message_data, message)
        self.assertEqual(response.system_data.data_type, 'text/plain')

    def test_pull_returns_type_json_when_sending_object(self):
        message = {"name": "message", "type": "object"}
        self.client.message_queue_push('af123', message)
        response = self.client.message_queue_pull()
        self.assertEqual(response.message_data, message)
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_pull_returns_type_octet_when_sending_binary(self):
        message = self.binary_fixture
        self.client.message_queue_push('af123', message)
        response = self.client.message_queue_pull()
        self.assertEqual(base64.b64decode(response.message_data), message)
        self.assertEqual(response.system_data.data_type, 'application/octet-stream')

    def test_pull_returns_custom_data_type_established_by_user(self):
        message = self.binary_fixture
        self.client.message_queue_push('af123', message, 'application/pdf')
        response = self.client.message_queue_pull()
        self.assertEqual(response.system_data.data_type, 'application/pdf')

    def test_pull_message_tries_are_one(self):
        message = {"name": "message", "type": "object"}
        self.client.message_queue_push('af123', message)
        response = self.client.message_queue_pull()
        self.assertEqual(int(response.system_data.tries), 1)


class MessageQueueAckInterfaceTest(SciroccoTestBase):
    def test_ack_message_status_changed(self):
        message = {"name": "message", "type": "object"}
        self.client.message_queue_push('af123', message)
        response_pull = self.client.message_queue_pull()
        response_ack = self.client.message_queue_ack(response_pull.system_data.id)
        self.assertEqual(response_ack.system_data.status, 'processed')

    def test_ack_message_processed_time_changed(self):
        message = {"name": "message", "type": "object"}
        self.client.message_queue_push('af123', message)
        response_pull = self.client.message_queue_pull()
        response_ack = self.client.message_queue_ack(response_pull.system_data.id)
        self.assertIsNotNone(response_ack.system_data.processed_time)

    def test_cannot_ack_message_that_not_previously_pulled(self):
        message = {"name": "message", "type": "object"}
        response_push = self.client.message_queue_push('af123', message)
        # response_pull = self.client.message_queue_pull()
        self.assertRaises(SciroccoHTTPDAOError, self.client.message_queue_ack, response_push.system_data.id)
