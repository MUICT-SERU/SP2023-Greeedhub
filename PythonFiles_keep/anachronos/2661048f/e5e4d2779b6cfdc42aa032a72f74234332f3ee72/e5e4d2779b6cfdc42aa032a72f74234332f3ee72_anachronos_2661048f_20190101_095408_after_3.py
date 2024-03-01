import multiprocessing

from anachronos.communication.anachronos import Anachronos


class AnachronosClient(Anachronos):

    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue

    def store(self, item):
        self.queue.put(item)
