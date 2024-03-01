import multiprocessing

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.exceptions import AnachronosException


class MessageQueueConsumer(object):

    def __init__(self, queue: multiprocessing.Queue, anachronos_server: MessageQueue):
        self.anachronos_server = anachronos_server
        self.queue = queue
        self.should_stop = False

    def listen(self):
        while not self.should_stop:
            if not self.queue.empty():
                message = self.queue.get(timeout=0.2)
                try:
                    self.anachronos_server.store(message)
                except AnachronosException:
                    self.stop()

    def stop(self):
        self.should_stop = True
