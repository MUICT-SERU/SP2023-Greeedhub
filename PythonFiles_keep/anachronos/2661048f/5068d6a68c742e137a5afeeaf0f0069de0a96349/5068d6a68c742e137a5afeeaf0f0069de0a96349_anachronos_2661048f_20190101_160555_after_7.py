from anachronos.test.assertion import Assertion


class UncaughtExceptionAssertion(Assertion):

    def __init__(self, exception):
        self.exception = exception

    def run(self, anachronos: "Anachronos"):
        self._do_assertion(False, f"Unexpected exception while running test. {self.exception}")
