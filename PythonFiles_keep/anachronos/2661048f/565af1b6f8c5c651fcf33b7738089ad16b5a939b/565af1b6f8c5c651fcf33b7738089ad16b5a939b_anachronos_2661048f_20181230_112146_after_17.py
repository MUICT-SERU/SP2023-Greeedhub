import multiprocessing

from multiprocessing import Process

from anachronos import setup_anachronos_client


class ApplicationRunner(object):

    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue
        self.process = Process(target=setup_and_run, args=(queue, self.app_run_function()))

    def run_app(self):
        self.process.start()

    def app_run_function(self):
        """Implement to return a function used to start your application."""
        raise NotImplementedError

    def stop(self):
        self.process.terminate()


def setup_and_run(queue, fun):
    setup_anachronos_client(queue)
    fun()
