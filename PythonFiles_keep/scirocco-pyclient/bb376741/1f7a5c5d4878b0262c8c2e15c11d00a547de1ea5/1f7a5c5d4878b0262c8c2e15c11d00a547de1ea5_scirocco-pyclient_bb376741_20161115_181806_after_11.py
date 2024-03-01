
class ClientMessageResponse:
    def __init__(self):
        self._metadata = None
        self._payload = None

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, data):
        self._metadata = data

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        self._payload = payload
