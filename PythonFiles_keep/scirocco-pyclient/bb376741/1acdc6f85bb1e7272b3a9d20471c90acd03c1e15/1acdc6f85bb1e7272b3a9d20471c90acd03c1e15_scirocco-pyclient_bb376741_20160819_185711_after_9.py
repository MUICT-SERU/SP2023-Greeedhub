from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientBatchResponse


class BatchDAO(Base):
    def __init__(self, request_adapter):
        super().__init__()
        self.request_adapter = request_adapter
        self.end_point = '/batches'

    def get_all(self):
        request_response = self.request_adapter.request('GET', self.end_point)
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def get_one(self, id):
        request_response = self.request_adapter.request('GET', ''.join([self.end_point, '/', id]))
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def delete_one(self, id):
        request_response = self.request_adapter.request('DELETE', ''.join([self.end_point, '/', id]))
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def delete_all(self):
        request_response = self.request_adapter.request('DELETE', self.end_point)
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def update_one(self, id, data):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', id]), data)
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError
