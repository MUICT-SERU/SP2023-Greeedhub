import multiprocessing

from anachronos.communication.logging_interfaces import _Anachronos


class AnachronosClient(_Anachronos):

    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue

    def store(self, item):
        self.queue.put(item)
