"""
TODO:

In system_data attribute , we need to create an object and inject it by composition.

We must ensure abstraction between system data client library and user program.

"""

class ClientMessageResponse:
    def __init__(self):
        self._system_data = None
        self._message_data = None

    @property
    def system_data(self):
        return self._system_data

    @system_data.setter
    def system_data(self, data):
        self._system_data = data

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, data):
        self._message_data = data


class ClientBatchResponse:
    def __init__(self):
        self._system_data = None
        self._messages_data = None

    @property
    def system_data(self):
        return self._system_data

    @system_data.setter
    def system_data(self, data):
        self._system_data = data

    @property
    def messages_data(self):
        return self._messages_data

    @messages_data.setter
    def messages_data(self, data):
        self._messages_data = data
