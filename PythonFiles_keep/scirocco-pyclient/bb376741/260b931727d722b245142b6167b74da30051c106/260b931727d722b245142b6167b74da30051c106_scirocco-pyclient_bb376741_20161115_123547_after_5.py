import base64
import os
import time
import datetime

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.messages import SciroccoMessage
from test.integration.base import SciroccoTestBase


class MessageQueuePushInterfaceTest(SciroccoTestBase):
    def test_push_text_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'This is my text message'

        response = self.client.message_queue_push(message)
        self.assertEqual(response.message_data, message.data)
        self.assertEqual(response.system_data.data_type, 'text/plain')

    def test_push_object_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}

        response = self.client.message_queue_push(message)
        self.assertEqual(response.message_data, message.data)
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_push_binary_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = self.binary_fixture

        response = self.client.message_queue_push(message)
        self.assertEqual(message.data, response.message_data)
        self.assertEqual(response.system_data.data_type, 'application/octet-stream')

    def test_push_custom_data_type_is_respected(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data_type = 'application/pdf'
        message.data = self.binary_fixture
        response = self.client.message_queue_push(message)
        self.assertEqual(response.system_data.data_type, 'application/pdf')

    def test_push_too_much_data_raises_error(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = os.urandom(1550000)

        self.assertRaises(SciroccoHTTPDAOError, self.client.message_queue_push, message)


class MessageSchedulingTest(SciroccoTestBase):
    def test_push_scheduled_time_message_in_past_raises_dao_exception(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'String message'
        message.scheduled_time = datetime.datetime.utcnow() - datetime.timedelta(seconds=1120)
        self.assertRaises(SciroccoHTTPDAOError, self.client.message_queue_push, message)

    def test_push_scheduled_message_inside_consuming_time_frame_returns_correctly(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'String message'
        message.scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
        self.client.message_queue_push(message)
        time.sleep(3)
        self.assertIsNotNone(self.client.message_queue_pull())

    def test_push_scheduled_time_message_in_future_is_not_available(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'String message'
        message.scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=234)
        self.client.message_queue_push(message)
        self.assertIsNone(self.client.message_queue_pull())


class MessageQueuePullInterfaceTest(SciroccoTestBase):
    def test_pull_returns_none_if_no_messages_pending(self):
        response = self.client.message_queue_pull()
        self.assertIsNone(response)

    def test_pull_returns_type_string_when_sending_string(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'This is my string test.'

        self.client.message_queue_push(message)
        response = self.client.message_queue_pull()
        self.assertEqual(response.message_data, message.data)
        self.assertEqual(response.system_data.data_type, 'text/plain')

    def test_pull_returns_type_json_when_sending_object(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}
        self.client.message_queue_push(message)
        response = self.client.message_queue_pull()
        self.assertEqual(response.message_data, message.data)
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_pull_returns_type_octet_when_sending_binary(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = self.binary_fixture

        self.client.message_queue_push(message)
        response = self.client.message_queue_pull()
        self.assertEqual(base64.b64decode(response.message_data), message.data)
        self.assertEqual(response.system_data.data_type, 'application/octet-stream')

    def test_pull_returns_custom_data_type_established_by_user(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data_type = 'application/pdf'
        message.data = self.binary_fixture

        self.client.message_queue_push(message)
        response = self.client.message_queue_pull()
        self.assertEqual(response.system_data.data_type, 'application/pdf')

    def test_pull_message_tries_are_one(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}
        self.client.message_queue_push(message)
        response = self.client.message_queue_pull()
        self.assertEqual(int(response.system_data.tries), 1)


class MessageQueueAckInterfaceTest(SciroccoTestBase):
    def test_ack_message_status_changed(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}

        self.client.message_queue_push(message)
        response_pull = self.client.message_queue_pull()
        response_ack = self.client.message_queue_ack(response_pull.system_data.id)
        self.assertEqual(response_ack.system_data.status, 'processed')

    def test_ack_message_processed_time_changed(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}

        self.client.message_queue_push(message)
        response_pull = self.client.message_queue_pull()
        response_ack = self.client.message_queue_ack(response_pull.system_data.id)
        self.assertIsNotNone(response_ack.system_data.processed_time)

    def test_cannot_ack_message_that_not_previously_pulled(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}
        response_push = self.client.message_queue_push(message)
        # response_pull = self.client.message_queue_pull()
        self.assertRaises(SciroccoHTTPDAOError, self.client.message_queue_ack, response_push.system_data.id)
