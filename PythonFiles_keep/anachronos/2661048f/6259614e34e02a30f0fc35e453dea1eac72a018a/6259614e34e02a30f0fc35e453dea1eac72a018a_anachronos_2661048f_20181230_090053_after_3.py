import threading

from anachronos import Anachronos


class AnachronosClient(Anachronos):

    def __init__(self, pipe_file: str):
        self.pipe_file = open(pipe_file, 'w')
        self.lock = threading.Lock()

    def store(self, item):
        with self.lock:
            self.pipe_file.write(item + "\n")

    def dispose(self):
        with self.lock:
            self.pipe_file.close()
