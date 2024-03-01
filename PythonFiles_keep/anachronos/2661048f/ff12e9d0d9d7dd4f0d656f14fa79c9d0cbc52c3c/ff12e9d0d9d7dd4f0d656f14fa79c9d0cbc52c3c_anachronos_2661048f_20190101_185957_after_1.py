import pkgutil

import anachronos.test.boot.test_case
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


TestCase = anachronos.test.boot.test_case.TestCase

run_tests = anachronos.test.boot.test_runner.run_tests


def discover_tests(test_package_root):
    prefix = test_package_root.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(test_package_root.__path__, prefix):
        module = __import__(modname, fromlist="dummy")
        if ispkg:
            discover_tests(module)
