import multiprocessing
from multiprocessing import Process

from anachronos.setup import setup_anachronos_client


class ApplicationRunner(object):

    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue
        self.process = Process(target=setup_and_run, args=(queue, self.app_run_function))

    def run(self):
        self.process.start()

    def app_run_function(self) -> None:
        """Implement to start your application. This is the main loop."""
        raise NotImplementedError

    def stop(self):
        self.process.terminate()


def setup_and_run(queue, fun):
    setup_anachronos_client(queue)
    fun()
