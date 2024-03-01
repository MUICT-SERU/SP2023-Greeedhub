from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientBatchResponse


class BatchQueueDAO(Base):
    def __init__(self, request_adapter):
        super().__init__()
        self.request_adapter = request_adapter
        self.end_point = '/batchQueue'

    def pull(self):
        request_response = self.request_adapter.request('GET', self.end_point)
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        elif request_response.http_status is 204:
            return None
        else:
            raise SystemError

    def push(self, batch):
        request_response = self.request_adapter.request('POST', self.end_point, batch)
        if request_response.http_status is 201:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def ack(self, batch_id):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', batch_id, '/ack']))
        if request_response.http_status is 200:
            ro = ClientBatchResponse()
            ro.system_data = request_response.system_data
            ro.messages_data = request_response.message_data
            return ro
        else:
            raise SystemError
