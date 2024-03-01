from queue import Queue, Empty

import time

from sciroccoclient.exceptions import SciroccoInterruptOnReceiveCallbackError
from sciroccoclient.messages import SciroccoMessage

from sciroccoclient.clients import HTTPClient
from test.integration.base import SciroccoTestBase


class ClientTests(SciroccoTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client_b = HTTPClient('http://localhost', 'af1234', 'DEFAULT_TOKEN')
        cls.queue = Queue()
    def setUp(self):
        super().setUp()
        while not self.queue.empty():
            try:
               self.queue.get(False)
            except Empty:
                continue
            self.queue.task_done()


    def client_callback(self, dao, msg):
        self.queue.put(msg)
        dao.ack(msg.metadata.id)

    def test_client_on_receive(self):
        message = SciroccoMessage()
        message.payload = {"type": "MESSAGE", "number": 0}
        message.node_destination = 'af1234'

        for m in range(10):
            message.payload['number'] = m
            self.client.push(message)
        on_receive_thread = self.client_b.on_receive(self.client_callback, True)
        counter = 0
        while self.queue.qsize() != 10:
            time.sleep(1)
            counter += 1
            if counter > 10:
                raise TimeoutError
        on_receive_thread.shutdown()
        self.assertEqual(self.queue.qsize(), 10)

    @staticmethod
    def client_callback2(dao, msg):
        dao.ack(msg.metadata.id)

        # We want to stop the tread if shutdown received.
        if msg.payload == 'shutdown':
            raise SciroccoInterruptOnReceiveCallbackError

    def test_client_on_receive_can_be_stopped_with_exception(self):
        on_receive_thread = self.client_b.on_receive(self.client_callback2, True)
        message = SciroccoMessage()
        message.node_destination = 'af1234'
        message.payload = 'shutdown'

        self.client.push(message)

        while on_receive_thread.is_alive():
            time.sleep(1)

        self.assertFalse(on_receive_thread.is_alive())








