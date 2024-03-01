from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientMessageResponse


class MessageDAO(Base):
    def __init__(self, request_adapter):
        super().__init__()
        self.request_adapter = request_adapter
        self.end_point = '/messages'

    def get_one(self, id):
        request_result = self.request_adapter.request('GET', ''.join([self.end_point, '/', id]))

        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data

            return ro
        else:
            raise SystemError

    def get_all(self):
        request_result = self.request_adapter.request('GET', self.end_point)

        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data

            return ro
        else:
            raise SystemError

    def delete_one(self, id):
        request_result = self.request_adapter.request('DELETE', ''.join([self.end_point, '/', id]))
        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data
            return ro
        else:
            raise SystemError

    def delete_all(self):
        request_result = self.request_adapter.request('DELETE', self.end_point)
        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data
            return ro

    def update_one(self, id, message):
        request_result = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', id]), message)
        if request_result.http_status is 200:
            ro = ClientMessageResponse()
            ro.system_data = request_result.system_data
            ro.message_data = request_result.message_data
            return ro
        else:
            raise SystemError
