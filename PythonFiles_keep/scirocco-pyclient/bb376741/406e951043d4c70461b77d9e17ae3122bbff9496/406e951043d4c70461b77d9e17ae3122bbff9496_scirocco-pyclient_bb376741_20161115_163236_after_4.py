import base64

from sciroccoclient.messages import SciroccoMessage
from sciroccoclient.responses import ClientMessageResponse
from test.integration.base import SciroccoTestBase


class MessagesGetOneInterfaceTest(SciroccoTestBase):
    def test_get_one_with_string_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'message'
        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, message.data)
        self.assertEqual(response_message_get.system_data.data_type, 'text/plain')

    def test_get_one_with_object_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, message.data)
        self.assertEqual(response_message_get.system_data.data_type, 'application/json')

    def test_get_one_with_binary_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = self.binary_fixture

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.system_data.id)
        self.assertEqual(base64.b64decode(response_message_get.message_data), message.data)
        self.assertEqual(response_message_get.system_data.data_type, 'application/octet-stream')

    def test_get_one_do_not_alter_anything_in_message(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'message'

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.system_data.id)
        self.assertEqual(response_message_get.message_data, response_message_get.message_data)
        self.assertEqual(str(sorted(response_push.system_data.__dict__)),
                         str(sorted(response_message_get.system_data.__dict__)))


class MessageGetAllInterfaceTest(SciroccoTestBase):
    def test_get_all_brings_all_pending_messages(self):
        for m in range(10):
            message = SciroccoMessage()
            message.destination = 'af123'
            message.data = 'This is message ' + str(m)
            self.client.push(message)
        messages_get = self.client.get_all()
        self.assertEqual(len(messages_get), 10)

    def test_get_all_messages_return_types(self):
        for m in range(10):
            message = SciroccoMessage()
            message.destination = 'af123'
            message.data = 'This is message ' + str(m)
            self.client.push(message)
        messages_get = self.client.get_all()
        for mg in messages_get:
            self.assertIsInstance(mg, ClientMessageResponse)

    def test_multiple_messages_different_payloads(self):

        message = SciroccoMessage()
        message.destination = 'af123'

        string_message = 'This message is type string.'
        object_message = {"name": "message", "type": "object"}
        binary_message = self.binary_fixture

        message.data = string_message
        self.client.push(message)

        message.data = object_message
        self.client.push(message)

        message.data = binary_message
        self.client.push(message)

        i = 1
        for m in self.client.get_all():
            if i == 1: self.assertEqual(m.message_data, string_message)
            if i == 2: self.assertEqual(m.message_data, object_message)
            if i == 3: self.assertEqual(base64.b64decode(m.message_data), binary_message)
            i = i + 1


class MessageDeleteOneInterfaceTest(SciroccoTestBase):
    def test_deletes_message_response(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'asd'
        message = self.client.push(message)
        delete_ops = self.client.delete_one(message.system_data.id)
        self.assertEqual(delete_ops.message_data['n'], 1)
        self.assertEqual(delete_ops.message_data['ok'], 1)

    def test_delete_only_the_message_specified(self):
        for m in range(10):
            message = SciroccoMessage()
            message.destination = 'af123'
            message.data = 'asd'
            last_message = self.client.push(message)

        self.client.delete_one(last_message.system_data.id)
        self.assertEqual(len(self.client.get_all()), 9)

    def test_empty_queue_after_message_deletion(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = 'asd'
        message = self.client.push(message)
        self.client.delete_one(message.system_data.id)
        self.assertIsNone(self.client.pull())


class MessageDeleteAllInterfaceTest(SciroccoTestBase):
    def test_response_stats(self):
        for m in range(10):
            message = SciroccoMessage()
            message.destination = 'af123'
            message.data = 'asd'
            self.client.push(message)
        response = self.client.delete_all()
        self.assertEqual(response.message_data['n'], 10)
        self.assertEqual(response.message_data['ok'], 1)

    def test_queue_empty_after_action(self):
        for m in range(10):
            message = SciroccoMessage()
            message.destination = 'af123'
            message.data = 'asd'
            self.client.push(message)
        self.client.delete_all()
        self.assertIsNone(self.client.pull())


class MessageUpdateOneInterfaceTest(SciroccoTestBase):
    def test_update_different_payload_type(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}
        pushed = self.client.push(message)
        new_message = self.binary_fixture
        response = self.client.update_one(pushed.system_data.id, new_message)
        self.assertEqual(new_message, base64.b64decode(response.message_data))
        self.assertEqual(response.system_data.data_type, 'application/json')

    def test_update_only_changes_payload(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}
        pushed = self.client.push(message)
        new_message = {"name": "messagechanged", "type": "object"}
        self.client.update_one(pushed.system_data.id, new_message)
        self.assertEqual(self.client.get(pushed.system_data.id).message_data['name'], 'messagechanged')

    def test_update_changes_update_time(self):
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message", "type": "object"}

        pushed = self.client.push(message)
        new_message = {"name": "messagechanged", "type": "object"}
        response = self.client.update_one(pushed.system_data.id, new_message)
        self.assertIsNotNone(response.system_data.update_time)
