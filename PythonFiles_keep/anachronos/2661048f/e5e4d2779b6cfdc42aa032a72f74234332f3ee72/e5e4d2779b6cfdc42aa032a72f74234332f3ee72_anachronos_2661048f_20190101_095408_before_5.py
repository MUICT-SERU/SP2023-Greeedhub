import anachronos
from anachronos import AnachronosClient


def setup_anachronos_client(queue):
    anachronos.anachronos = AnachronosClient(queue)



