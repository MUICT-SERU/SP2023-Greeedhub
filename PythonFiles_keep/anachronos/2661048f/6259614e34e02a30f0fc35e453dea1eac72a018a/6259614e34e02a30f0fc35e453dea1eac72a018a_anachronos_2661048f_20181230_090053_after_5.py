import threading

from anachronos.application_runner import ApplicationRunner
from anachronos.remote.anachronos_server import AnachronosServer


class TestRunner(object):

    def __init__(self, application_runner: ApplicationRunner, anachronos_server: AnachronosServer):
        self.server_thread = threading.Thread(target=anachronos_server.listen)
        self.application_thread = threading.Thread(target=application_runner.run_app)

    def run(self):
        self.server_thread.start()



