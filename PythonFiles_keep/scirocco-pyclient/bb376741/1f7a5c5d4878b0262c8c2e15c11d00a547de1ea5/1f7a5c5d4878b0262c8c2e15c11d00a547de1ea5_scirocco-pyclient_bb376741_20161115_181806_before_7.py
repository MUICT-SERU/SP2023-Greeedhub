from sciroccoclient.exceptions import SciroccoHTTPDAOError, SciroccoInvalidMessageError, \
    SciroccoInvalidMessageDataError, SciroccoInvalidMessageDestinationError, SciroccoInvalidMessageStatusError
from sciroccoclient.http.base import Base
from sciroccoclient.messages import SciroccoMessage
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
            raise SciroccoHTTPDAOError(request_response.http_status)

    def push(self, message):
        # Todo , next refactor, move this to its own validator class.
        if not isinstance(message, SciroccoMessage):
            raise SciroccoInvalidMessageError
        if not message.destination:
            raise SciroccoInvalidMessageDestinationError
        if not message.status:
            raise SciroccoInvalidMessageStatusError
        if not message.data:
            raise SciroccoInvalidMessageDataError

        headers = {
            self.system_data_descriptor.get_http_header_by_field_name('to'): message.destination,
            self.system_data_descriptor.get_http_header_by_field_name('status'): message.status
        }

        if message.data_type:
            headers.update({self.system_data_descriptor.get_http_header_by_field_name('data_type'): message.data_type
                            })
        if message.status == 'scheduled' and message.scheduled_time:
            headers.update(
                {self.system_data_descriptor.get_http_header_by_field_name('scheduled_time'): message.scheduled_time})

        request_response = self.request_adapter.request('POST', self.end_point, message.data, headers)

        if request_response.http_status is 201:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)

    def ack(self, msg_id):
        request_response = self.request_adapter.request('PATCH', ''.join([self.end_point, '/', msg_id, '/ack']))

        if request_response.http_status == 200:
            ro = ClientMessageResponse()
            ro.system_data = request_response.system_data
            ro.message_data = request_response.message_data
            return ro
        else:
            raise SciroccoHTTPDAOError(request_response.http_status)
