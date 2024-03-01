import base64
import unittest

from sciroccoclient.responses import ClientMessageResponse
from test.integration.base import SciroccoTestBase


class MessagesGetOneInterfaceTest(SciroccoTestBase):
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


class MessageGetAllInterfaceTest(SciroccoTestBase):
    def test_get_all_brings_all_pending_messages(self):
        for m in range(10):
            self.client.message_queue_push('af123', 'This is message ' + str(m))
        messages_get = self.client.message_get_all()
        self.assertEqual(len(messages_get), 10)

    def test_get_all_messages_return_types(self):
        for m in range(10):
            self.client.message_queue_push('af123', 'This is message ' + str(m))
        messages_get = self.client.message_get_all()
        for mg in messages_get:
            self.assertIsInstance(mg, ClientMessageResponse)

    def test_multiple_messages_different_payloads(self):

        string_message = 'This message is type string.'
        object_message = {"name": "message", "type": "object"}
        binary_message = self.binary_fixture

        self.client.message_queue_push('af123', string_message)
        self.client.message_queue_push('af123', object_message)
        self.client.message_queue_push('af123', binary_message)
        i = 1
        for m in self.client.message_get_all():
            if i == 1: self.assertEqual(m.message_data, string_message)
            if i == 2: self.assertEqual(m.message_data, object_message)
            if i == 3: self.assertEqual(base64.b64decode(m.message_data), binary_message)
            i = i + 1


class MessageDeleteOneInterfaceTest(SciroccoTestBase):
    def test_deletes_message_response(self):
        message = self.client.message_queue_push('af123', 'message')
        delete_ops = self.client.message_delete_one(message.system_data.id)
        self.assertEqual(delete_ops.message_data['n'], 1)
        self.assertEqual(delete_ops.message_data['ok'], 1)

    def test_delete_only_the_message_specified(self):
        for m in range(10):
            last_message = self.client.message_queue_push('af123', 'message')

        self.client.message_delete_one(last_message.system_data.id)
        self.assertEqual(len(self.client.message_get_all()), 9)

    def test_empty_queue_after_message_deletion(self):
        message = self.client.message_queue_push('af123', 'message')
        self.client.message_delete_one(message.system_data.id)
        self.assertIsNone(self.client.message_queue_pull())


class MessageDeleteAllInterfaceTest(SciroccoTestBase):
    def test_response_stats(self):
        for m in range(10):
            self.client.message_queue_push('af123', 'message')
        response = self.client.message_delete_all()
        self.assertEqual(response.message_data['n'], 10)
        self.assertEqual(response.message_data['ok'], 1)

    def test_queue_empty_after_action(self):
        for m in range(10):
            self.client.message_queue_push('af123', 'message')
        self.client.message_delete_all()
        self.assertIsNone(self.client.message_queue_pull())


class MessageUpdateOneInterfaceTest(SciroccoTestBase):
    def test_update_different_payload_type(self):
        message = {"name": "message", "type": "object"}
        pushed = self.client.message_queue_push('af123', message)
        new_message = self.binary_fixture
        response = self.client.message_update_one(pushed.system_data.id, new_message)
        self.assertEqual(new_message, base64.b64decode(response.message_data))
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_update_only_changes_payload(self):
        message = {"name": "message", "type": "object"}
        pushed = self.client.message_queue_push('af123', message)
        new_message = {"name": "messagechanged", "type": "object"}
        self.client.message_update_one(pushed.system_data.id, new_message)
        self.assertEqual(self.client.message_get(pushed.system_data.id).message_data['name'], 'messagechanged')

    def test_update_changes_update_time(self):
        message = {"name": "message", "type": "object"}
        pushed = self.client.message_queue_push('af123', message)
        new_message = {"name": "messagechanged", "type": "object"}
        response = self.client.message_update_one(pushed.system_data.id, new_message)
        self.assertIsNotNone(response.system_data.update_time)
