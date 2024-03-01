import base64

from sciroccoclient.messages import SciroccoMessage
from sciroccoclient.responses import ClientMessageResponse
from test.integration.base import SciroccoTestBase


class MessagesGetOneInterfaceTest(SciroccoTestBase):
    def test_get_one_with_string_payload(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = 'message'
        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.metadata.id)
        self.assertEqual(response_message_get.payload, message.payload)
        self.assertEqual(response_message_get.metadata.payload_type, 'text/plain')

    def test_get_one_with_object_payload(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = {"name": "message", "type": "object"}

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.metadata.id)
        self.assertEqual(response_message_get.payload, message.payload)
        self.assertEqual(response_message_get.metadata.payload_type, 'application/json')

    def test_get_one_with_binary_payload(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = self.binary_fixture

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.metadata.id)
        self.assertEqual(base64.b64decode(response_message_get.payload), message.payload)
        self.assertEqual(response_message_get.metadata.payload_type, 'application/octet-stream')

    def test_get_one_do_not_alter_anything_in_message(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = 'message'

        response_push = self.client.push(message)
        response_message_get = self.client.get(response_push.metadata.id)
        self.assertEqual(response_message_get.payload, response_message_get.payload)
        self.assertEqual(str(sorted(response_push.metadata.__dict__)),
                         str(sorted(response_message_get.metadata.__dict__)))


class MessageGetAllInterfaceTest(SciroccoTestBase):
    def test_get_all_brings_all_pending_messages(self):
        for m in range(10):
            message = SciroccoMessage()
            message.node_destination = 'af123'
            message.payload = 'This is message ' + str(m)
            self.client.push(message)
        messages_get = self.client.get_all()
        self.assertEqual(len(messages_get), 10)

    def test_get_all_messages_return_types(self):
        for m in range(10):
            message = SciroccoMessage()
            message.node_destination = 'af123'
            message.payload = 'This is message ' + str(m)
            self.client.push(message)
        messages_get = self.client.get_all()
        for mg in messages_get:
            self.assertIsInstance(mg, ClientMessageResponse)

    def test_multiple_messages_different_payloads(self):

        message = SciroccoMessage()
        message.node_destination = 'af123'

        string_message = 'This message is type string.'
        object_message = {"name": "message", "type": "object"}
        binary_message = self.binary_fixture

        message.payload = string_message
        self.client.push(message)

        message.payload = object_message
        self.client.push(message)

        message.payload = binary_message
        self.client.push(message)

        i = 1
        for m in self.client.get_all():
            if i == 1: self.assertEqual(m.payload, string_message)
            if i == 2: self.assertEqual(m.payload, object_message)
            if i == 3: self.assertEqual(base64.b64decode(m.payload), binary_message)
            i = i + 1


class MessageDeleteOneInterfaceTest(SciroccoTestBase):
    def test_deletes_message_response(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = 'asd'
        message = self.client.push(message)
        delete_ops = self.client.delete_one(message.metadata.id)
        self.assertEqual(delete_ops.payload['n'], 1)
        self.assertEqual(delete_ops.payload['ok'], 1)

    def test_delete_only_the_message_specified(self):
        for m in range(10):
            message = SciroccoMessage()
            message.node_destination = 'af123'
            message.payload = 'asd'
            last_message = self.client.push(message)

        self.client.delete_one(last_message.metadata.id)
        self.assertEqual(len(self.client.get_all()), 9)

    def test_empty_queue_after_message_deletion(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = 'asd'
        message = self.client.push(message)
        self.client.delete_one(message.metadata.id)
        self.assertIsNone(self.client.pull())


class MessageDeleteAllInterfaceTest(SciroccoTestBase):
    def test_response_stats(self):
        for m in range(10):
            message = SciroccoMessage()
            message.node_destination = 'af123'
            message.payload = 'asd'
            self.client.push(message)
        response = self.client.delete_all()
        self.assertEqual(response.payload['n'], 10)
        self.assertEqual(response.payload['ok'], 1)

    def test_queue_empty_after_action(self):
        for m in range(10):
            message = SciroccoMessage()
            message.node_destination = 'af123'
            message.payload = 'asd'
            self.client.push(message)
        self.client.delete_all()
        self.assertIsNone(self.client.pull())


class MessageUpdateOneInterfaceTest(SciroccoTestBase):
    def test_update_different_payload_type(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = {"name": "message", "type": "object"}
        pushed = self.client.push(message)
        new_message = self.binary_fixture
        response = self.client.update_one(pushed.metadata.id, new_message)
        self.assertEqual(new_message, base64.b64decode(response.payload))
        self.assertEqual(response.metadata.payload_type, 'application/json')

    def test_update_only_changes_payload(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = {"name": "message", "type": "object"}
        pushed = self.client.push(message)
        new_message = {"name": "messagechanged", "type": "object"}
        self.client.update_one(pushed.metadata.id, new_message)
        self.assertEqual(self.client.get(pushed.metadata.id).payload['name'], 'messagechanged')

    def test_update_changes_update_time(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = {"name": "message", "type": "object"}

        pushed = self.client.push(message)
        new_message = {"name": "messagechanged", "type": "object"}
        response = self.client.update_one(pushed.metadata.id, new_message)
        self.assertIsNotNone(response.metadata.update_time)
