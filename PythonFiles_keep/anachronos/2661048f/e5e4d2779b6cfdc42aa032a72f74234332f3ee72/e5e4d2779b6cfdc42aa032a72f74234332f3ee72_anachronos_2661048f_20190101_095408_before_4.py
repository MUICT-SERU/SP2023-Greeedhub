import multiprocessing

import time

from anachronos.anachronos import MessageQueue


class MessageQueueConsumer(object):

    def __init__(self, queue: multiprocessing.Queue, anachronos_server: MessageQueue):
        self.anachronos_server = anachronos_server
        self.queue = queue
        self.should_stop = False

    def listen(self):
        while not self.should_stop:
            if not self.queue.empty():
                message = self.queue.get(timeout=0.5)
                self.anachronos_server.store(message)
            else:
                time.sleep(0.2)

    def stop(self):
        self.should_stop = True
