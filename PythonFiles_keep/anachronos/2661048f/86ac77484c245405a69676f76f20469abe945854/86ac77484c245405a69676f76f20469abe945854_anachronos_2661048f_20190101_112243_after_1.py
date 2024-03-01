import anachronos.test.boot.test_runner
from anachronos.communication.logging_interfaces import _Anachronos

__version__ = '@@VERSION@@'

Anachronos = _Anachronos

_instance = None


def get_instance():
    return _instance


def set_instance(instance):
    global _instance
    _instance = instance


TestCase = anachronos.test.boot.test_runner.TestCase

run_tests = anachronos.test.boot.test_runner.run_tests
