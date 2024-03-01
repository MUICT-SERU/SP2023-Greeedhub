from anachronos.anachronos import Anachronos
from anachronos.communication.anachronos_client import AnachronosClient

__version__ = '@@VERSION@@'

anachronos = None


def setup_anachronos_client(queue):
    global anachronos
    anachronos = AnachronosClient(queue)
