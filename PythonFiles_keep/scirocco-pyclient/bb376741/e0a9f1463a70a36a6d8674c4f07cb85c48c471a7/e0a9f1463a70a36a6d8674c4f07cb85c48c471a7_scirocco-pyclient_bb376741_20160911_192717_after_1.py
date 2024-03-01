from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientMessageResponse


class MessageQueueDAO(Base):
    def __init__(self, request_adapter):
        super().__init__()
        self.request_adapter = request_adapter
        self.end_point = '/messageQueue'

    def pull(self):

        request_response = self.request_adapter.request('GET', self.end_point)

        if request_response.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data

            return ro
        elif request_response.http_status is 204:
            return None
        else:
            raise SystemError

    def push(self, msg):
        request_response = self.request_adapter.request('POST', self.end_point, msg)

        if request_response.http_status is 201:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SystemError

    def ack(self, msg_id):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', msg_id, '/ack']))

        if request_response.http_status == 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SystemError
