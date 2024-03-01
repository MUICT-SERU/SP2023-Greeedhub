import json


class DataTypeConverter:
    def convert_to_dict(self, data):

        if isinstance(data, str):
            data = json.loads(data)
        elif isinstance(data, bytes):
            data = json.loads(data.decode("utf8"))
        elif isinstance(data, dict):
            pass
        else:
            raise TypeError

        return data


class RequestResponse:
    def __init__(self):
        self.converter = DataTypeConverter()
        self._system_data = None
        self._message_data = None
        self._http_headers = None

    @property
    def system_data(self):
        return self._system_data

    @system_data.setter
    def system_data(self, data):
        self._system_data = self.converter.convert_to_dict(data)

    @property
    def message_data(self):
        return self._message_data

    @message_data.setter
    def message_data(self, data):
        self._message_data = self.converter.convert_to_dict(data)

    @property
    def http_headers(self):
        return self._http_headers

    @http_headers.setter
    def http_headers(self, data):
        self._http_headers = self.converter.convert_to_dict(data)
