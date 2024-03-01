from sciroccoclient.http.base import Base
from sciroccoclient.responses import ClientMessageResponse


class MessageQueueDAO(Base):
    def __init__(self, request_adapter, system_data_descriptor):
        super().__init__()
        self.request_adapter = request_adapter
        self.system_data_descriptor = system_data_descriptor
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

    def push(self, destination, msg, scirocco_type):

        headers = { self.system_data_descriptor.get_by_name('to'): destination }

        if scirocco_type:
            headers.update({self.system_data_descriptor.get_by_name('data_type'): scirocco_type
                            })

        request_response = self.request_adapter.request('POST', self.end_point, msg, headers)

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
