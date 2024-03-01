import anachronos.communication.anachronos
from anachronos.test.boot import test_runner

__version__ = '@@VERSION@@'

Anachronos = anachronos.communication.anachronos.Anachronos

_instance = None

def get_instance():
    return _instance

def set_instance(instance):
    global _instance
    _instance = instance

TestCase = test_runner.TestCase
